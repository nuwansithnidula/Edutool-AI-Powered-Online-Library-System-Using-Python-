from utils.bd import Database
from datetime import datetime

class HistoryModel:
    @staticmethod
    def _col():
        db = Database.get_instance()
        return db['history']

    @staticmethod
    def save_history(user_id, book_id):
        return HistoryModel._col().update_one(
            {"user_id": str(user_id), "book_id": str(book_id)},
            {"$set": {"last_read_at": datetime.now()}},
            upsert=True 
        )

    @staticmethod
    def get_user_history(user_id):
        return list(HistoryModel._col().find({"user_id": str(user_id)}).sort("last_read_at", -1))

    @staticmethod
    def remove_from_history(user_id, book_id):
        return HistoryModel._col().delete_one({"user_id": str(user_id), "book_id": str(book_id)})

    @staticmethod
    def get_most_read_books(limit=12):
        pipeline = [
            {"$group": {"_id": "$book_id", "read_count": {"$sum": 1}}},
            {"$sort": {"read_count": -1}}, 
            {"$limit": limit} 
        ]
        return list(HistoryModel._col().aggregate(pipeline))