import numpy as np
from Database.config import faces_collection
from ML.similarity import predict_with_cosine

THRESHOLD = 0.40  # Cosine similarity threshold

def _get_all_records():
    records = list(faces_collection.find({}))
    if not records:
        return [], []
    db_embeddings = [np.array(r["embedding"]) for r in records]
    names = [r["name"] for r in records]
    return db_embeddings, names

def find_match(embedding):
    """
    Finds the closest match using Cosine Similarity against all known faces.
    """
    db_embeddings, names = _get_all_records()
    
    if not db_embeddings:
        return None, 0.0
        
    best_name, best_score = predict_with_cosine(embedding, db_embeddings, names)
    
    if best_score >= THRESHOLD:
        return best_name, best_score
    return None, best_score

def save_face(name, embedding):
    """
    Saves a new face embedding to the database.
    """
    faces_collection.insert_one({"name": name, "embedding": embedding.tolist()})
