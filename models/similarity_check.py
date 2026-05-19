import numpy as np
import math

# InsightFace Cosine Distance threshold: 0.60
# (same person = cosine distance <= 0.60, equivalent to cosine similarity >= 0.40)
DISTANCE_THRESHOLD = 0.60

# Minimum fraction of stored encodings that must agree on a match
MIN_VOTE_RATIO = 0.40  # at least 40% of a person's encodings must match


def face_distance_to_conf(face_distance, face_match_threshold=DISTANCE_THRESHOLD):
    """
    Convert Euclidean distance → confidence percentage using a non-linear curve.
    Distance 0.0  → 100%  (exact same image)
    Distance 0.50 → ~75%  (at threshold)
    Distance 1.0  → 0%    (completely different)
    """
    if face_distance > face_match_threshold:
        dist_range = 1.0 - face_match_threshold
        linear_val = (1.0 - face_distance) / (dist_range * 2.0)
        return max(0.0, linear_val * 100)
    else:
        dist_range = face_match_threshold
        linear_val = 1.0 - (face_distance / (dist_range * 2.0))
        curved = linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))
        return curved * 100


def _compare_against_person(db_embeddings, new_emb, threshold):
    """
    Compare one new embedding against all stored embeddings for one person.
    Returns:
        best_dist   - lowest distance found
        avg_dist    - average distance across all stored embeddings
        vote_count  - how many stored embeddings matched (dist <= threshold)
        vote_ratio  - vote_count / total stored embeddings
    """
    distances = []
    for db_emb in db_embeddings:
        db_emb_np = np.array(db_emb)
        # Gracefully handle legacy 128-d database records to avoid ValueErrors
        if db_emb_np.shape != new_emb.shape:
            continue
        cos_sim = np.dot(db_emb_np, new_emb) / (
                    np.linalg.norm(db_emb_np) * np.linalg.norm(new_emb)
                )
        # Cosine distance = 1.0 - Cosine Similarity.
        # Smaller distance (closer to 0.0) means higher similarity (closer to 1.0).
        dist = 1.0 - cos_sim
        distances.append(dist)

    if not distances:
        return float('inf'), float('inf'), 0, 0.0

    distances = np.array(distances)
    best_dist  = float(np.min(distances))
    avg_dist   = float(np.mean(distances))
    vote_count = int(np.sum(distances <= threshold))
    vote_ratio = vote_count / len(distances) if len(distances) > 0 else 0.0

    return best_dist, avg_dist, vote_count, vote_ratio


def ml_face_embedding_check(all_embedding, new_face_embeddings):
    """
    Checks if any of the new face embeddings match a registered person.

    Args:
        all_embedding:      List of DB records, each with 'name' and 'embedding' (list of 128-d vectors)
        new_face_embeddings: List of new 128-d vectors (can be multiple from multi-jitter or multi-face)

    Returns:
        is_new_face (bool), matched_name (str|None), confidence (float)
    """
    if not all_embedding:
        print("[!] No registered faces in database — treating as new face.")
        return True, None, 0.0

    if not new_face_embeddings:
        print("[!] No face embeddings provided.")
        return True, None, 0.0

    # ✅ FIX: Support multiple new embeddings (average them for robustness)
    new_emb = np.mean([np.array(e) for e in new_face_embeddings], axis=0)

    best_match_name  = None
    best_distance    = float('inf')
    best_confidence  = 0.0
    best_vote_ratio  = 0.0

    print(f"\n[*] Comparing against {len(all_embedding)} registered user(s)...")
    print("=" * 65)
    print(f"{'Name':<20} | {'Best Dist':<10} | {'Avg Dist':<10} | {'Votes':<10} | {'Conf':<8}")
    print("-" * 65)

    for record in all_embedding:
        person_name  = record.get('name', str(record.get('_id', 'unknown')))
        db_embeddings = record.get('embedding', [])

        if not db_embeddings:
            print(f"{person_name:<20} | {'NO DATA'}")
            continue

        best_dist, avg_dist, vote_count, vote_ratio = _compare_against_person(
            db_embeddings, new_emb, DISTANCE_THRESHOLD
        )

        conf = face_distance_to_conf(best_dist)
        vote_str = f"{vote_count}/{len(db_embeddings)} ({vote_ratio:.0%})"

        print(f"{person_name:<20} | {best_dist:<10.4f} | {avg_dist:<10.4f} | {vote_str:<10} | {conf:.2f}%")

        # ✅ FIX: Use BOTH distance AND vote ratio for selection
        # Prioritize vote ratio first (consensus), then distance as tiebreaker
        is_better = (
            vote_ratio > best_vote_ratio or
            (vote_ratio == best_vote_ratio and best_dist < best_distance)
        )

        if is_better:
            best_distance   = best_dist
            best_match_name = person_name
            best_confidence = conf
            best_vote_ratio = vote_ratio

    print("=" * 65)
    print(f"[*] Best candidate: '{best_match_name}' | dist={best_distance:.4f} | votes={best_vote_ratio:.0%} | conf={best_confidence:.2f}%")

    # ✅ FIX: Dual condition — must pass BOTH distance AND vote ratio
    distance_ok   = best_distance  <= DISTANCE_THRESHOLD
    vote_ratio_ok = best_vote_ratio >= MIN_VOTE_RATIO

    if distance_ok and vote_ratio_ok:
        print(f"[+] ✅ Match confirmed → '{best_match_name}' verified! (dist={best_distance:.4f}, votes={best_vote_ratio:.0%})")
        return False, best_match_name, best_confidence

    elif distance_ok and not vote_ratio_ok:
        print(f"[~] ⚠️  Distance OK but weak consensus ({best_vote_ratio:.0%} < {MIN_VOTE_RATIO:.0%}) → treating as new face")
        return True, None, best_confidence

    else:
        print(f"[-] ❌ No match. Distance {best_distance:.4f} > threshold {DISTANCE_THRESHOLD} → New face")
        return True, None, best_confidence