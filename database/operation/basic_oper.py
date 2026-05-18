from database.config.config import db
from models.similarity_check import ml_face_embedding_check

def get_all_face_data(new_face_embedding):
    """
    Check if a face embedding already exists in the database.
    
    Returns:
        tuple: (is_new_face: bool, matched_name: str or None)
            - (True, None)          → new face, not in database
            - (False, "person_name", 99.9) → face already registered
    """

    collection = list(db['ImageEmbedding'].find({}, {'embedding': 1, 'name': 1, "_id": 1}))

    is_new_face, matched_name, confidence = ml_face_embedding_check(collection, new_face_embedding)

    return is_new_face, matched_name, confidence

    


