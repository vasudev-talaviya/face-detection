import pymongo
from dotenv import load_dotenv
import os

load_dotenv()

URL = os.getenv("MONGODB_URL")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME")

client = pymongo.MongoClient(URL)

db = client[MONGODB_DATABASE_NAME]