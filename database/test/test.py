from config import db
from models.faceid import UserModel

data = {"embedding":[1,2,4,213,12,312,321,3,213],
"name":'vasudev',
}

user = UserModel(**data)

check = db['ImageEmbedding'].insert_one(user.model_dump())
print(db['ImageEmbedding'].find_one())


if True:

    delete_id = db['ImageEmbedding'].delete_one({"_id":check.inserted_id})
    print("Delete confirmation:-",delete_id.deleted_count)