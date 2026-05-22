from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("MONGO_URI")
client = MongoClient(uri)
db = client["trading_db"]

print("Connection ok:", db.list_collection_names())