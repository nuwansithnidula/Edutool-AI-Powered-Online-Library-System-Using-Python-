from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

class Database:
    _instance = None

    @staticmethod
    def get_instance():
        """Singleton Pattern: Only one connection is created to the database."""
        if Database._instance is None:
            client = MongoClient(MONGO_URI)
            Database._instance = client[DB_NAME]
        return Database._instance