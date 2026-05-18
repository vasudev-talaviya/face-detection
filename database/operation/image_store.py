from database.models.faceid import UserModel
from database.config.config import db

def insert_new_user(embedding, name):
    """
    Directly insert a new user without duplicate checking.
    (Duplicate checking is done as an early checkpoint in main.py)
    """

    data = {"name":name,
            "embedding":embedding}
    
    validation_check = UserModel(**data)

    if validation_check:

        # insert the database
        try:
            collection = db['ImageEmbedding']

            database_insert = collection.insert_one(validation_check.model_dump())

            if database_insert.inserted_id:
                print("🎉 Congratulation inserted your record...")
                return True
            else:
                print("❌ Sorry not inserted try again...")
                return False
            
        except Exception as e:
            print(f"Error happening: {e}")
            exit()