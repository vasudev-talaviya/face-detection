import math
from dataclasses import dataclass

import numpy as np

# InsightFace cosine distance threshold: lower means more similar.
DISTANCE_THRESHOLD = 0.60
MIN_VOTE_RATIO = 0.40


@dataclass(frozen=True)
class MatchResult:
    is_new_face: bool
    name: str | None
    confidence: float
    user_id: str | None = None


def face_distance_to_conf(face_distance: float, face_match_threshold: float = DISTANCE_THRESHOLD) -> float:
    """Convert a cosine distance into a UI-friendly confidence percentage."""
    if not math.isfinite(face_distance):
        return 0.0
    if face_distance > face_match_threshold:
        distance_range = 1.0 - face_match_threshold
        linear_value = (1.0 - face_distance) / (distance_range * 2.0)
        return max(0.0, linear_value * 100)
    distance_range = face_match_threshold
    linear_value = 1.0 - (face_distance / (distance_range * 2.0))
    curved = linear_value + ((1.0 - linear_value) * math.pow((linear_value - 0.5) * 2, 0.2))
    return curved * 100


def _compare_against_person(
    stored_embeddings: list[list[float]],
    new_embedding: np.ndarray,
    threshold: float,
) -> tuple[float, float]:
    distances = []
    new_norm = np.linalg.norm(new_embedding)
    if new_norm == 0:
        return float("inf"), 0.0

    for stored_embedding in stored_embeddings:
        stored = np.asarray(stored_embedding, dtype=float)
        stored_norm = np.linalg.norm(stored)
        if stored.shape != new_embedding.shape or stored_norm == 0:
            continue
        similarity = np.dot(stored, new_embedding) / (stored_norm * new_norm)
        distances.append(1.0 - similarity)

    if not distances:
        return float("inf"), 0.0
    distance_values = np.asarray(distances)
    vote_ratio = float(np.sum(distance_values <= threshold) / len(distance_values))
    return float(np.min(distance_values)), vote_ratio


def _match(all_embeddings: list[dict], new_face_embeddings: list[list[float]]) -> MatchResult:
    if not all_embeddings or not new_face_embeddings:
        return MatchResult(True, None, 0.0)

    new_embedding = np.mean([np.asarray(value, dtype=float) for value in new_face_embeddings], axis=0)
    best_name = None
    best_id = None
    best_distance = float("inf")
    best_vote_ratio = 0.0

    for record in all_embeddings:
        distance, vote_ratio = _compare_against_person(
            record.get("embedding", []),
            new_embedding,
            DISTANCE_THRESHOLD,
        )
        better_match = vote_ratio > best_vote_ratio or (
            vote_ratio == best_vote_ratio and distance < best_distance
        )
        if better_match:
            best_name = record.get("name", str(record.get("_id", "unknown")))
            best_id = str(record["_id"]) if record.get("_id") is not None else None
            best_distance = distance
            best_vote_ratio = vote_ratio

    confidence = face_distance_to_conf(best_distance)
    matches = best_distance <= DISTANCE_THRESHOLD and best_vote_ratio >= MIN_VOTE_RATIO
    if matches:
        return MatchResult(False, best_name, confidence, best_id)
    return MatchResult(True, None, confidence)


def ml_face_embedding_check_with_id(all_embedding, new_face_embeddings):
    result = _match(all_embedding, new_face_embeddings)
    return result.is_new_face, result.name, result.confidence, result.user_id
