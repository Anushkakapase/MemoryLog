from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["memorylog"]

users_collection = db["users"]

history_collection = db["history"]

location_collection = db["locations"]