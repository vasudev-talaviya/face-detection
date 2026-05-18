import numpy as np
import math

# Dlib's official threshold for face recognition is 0.6.
# A Euclidean distance strictly less than 0.6 means it's the same person.
# We use 0.55 here for slightly stricter matching to prevent false positives.
DISTANCE_THRESHOLD = 0.55

def face_distance_to_conf(face_distance, face_match_threshold=DISTANCE_THRESHOLD):
    """
    Convert Euclidean distance to a percentage probability confidence score.
    Using non-linear curve to map distance more like a probability.
    """
    if face_distance > face_match_threshold:
        dist_range = (1.0 - face_match_threshold)
        linear_val = (1.0 - face_distance) / (dist_range * 2.0)
        return max(0.0, linear_val * 100)
    else:
        dist_range = face_match_threshold
        linear_val = 1.0 - (face_distance / (dist_range * 2.0))
        # Add curve
        return (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100

def ml_face_embedding_check(all_embedding, new_face_embedding):
    """
    Checks if the new face embedding matches any existing faces in the database
    using Euclidean distance. Also calculates and shows probability scores.
    """
    if not all_embedding or len(all_embedding) == 0:
        print("[!] No registered faces in database — this is a new face.")
        return True, None, 0.0

    new_emb = np.array(new_face_embedding[0])
    
    best_match_name = None
    best_distance = float('inf')
    best_confidence = 0.0

    print(f"\n[*] Comparing new face against {len(all_embedding)} registered user(s)...")
    print("-" * 45)
    print(f"{'Name':<20} | {'Distance':<10} | {'Probability':<10}")
    print("-" * 45)

    for record in all_embedding:
        person_name = record.get('name', str(record['_id']))
        db_embeddings = record.get('embedding', [])
        
        # Calculate for each person
        person_best_dist = float('inf')
        for db_emb in db_embeddings:
            db_emb_np = np.array(db_emb)
            # Dlib is optimized for Euclidean distance (L2 distance)
            dist = np.linalg.norm(db_emb_np - new_emb)
            if dist < person_best_dist:
                person_best_dist = dist
        
        person_conf = face_distance_to_conf(person_best_dist)
        
        # Display the score for each user
        print(f"{person_name:<20} | {person_best_dist:<10.4f} | {person_conf:.2f}%")

        if person_best_dist < best_distance:
            best_distance = person_best_dist
            best_match_name = person_name
            best_confidence = person_conf

    print("-" * 45)
    print(f"[*] Best match: '{best_match_name}' with {best_confidence:.2f}% probability (Dist: {best_distance:.4f})")

    # If the distance is below the threshold, it's a match!
    # Distance of 0.0 means it is the EXACT same image.
    if best_distance <= DISTANCE_THRESHOLD:
        print(f"[+] Match confirmed -> Name: '{best_match_name}' is verified!")
        return False, best_match_name, best_confidence
    else:
        print(f"[-] No match found. Probability is too low ({best_confidence:.2f}%). -> New face")
        return True, None, best_confidence