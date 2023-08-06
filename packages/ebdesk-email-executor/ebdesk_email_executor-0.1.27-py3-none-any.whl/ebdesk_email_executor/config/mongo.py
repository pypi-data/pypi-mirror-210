from pymongo import MongoClient


def connect():
    client = MongoClient(
        "mongodb://rizalwidiatmaja:R1z4lM0ngoD3B@10.12.1.91:27017/?retryWrites=true&serverSelectionTimeoutMS=5000&connectTimeoutMS=10000&authSource=admin&authMechanism=SCRAM-SHA-1")
    db = client["executor-account"]
    collection = db["email"]
    return collection
