from pydantic import BaseModel,EmailStr
from typing import List 

class UserModel(BaseModel):
    

    name : str
    embedding : List[List[float]]