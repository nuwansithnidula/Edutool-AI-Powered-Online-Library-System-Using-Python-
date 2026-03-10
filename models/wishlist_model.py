from datetime import datetime
from bson import ObjectId
from utils.bd import Database
from config import WISHLIST_COLLECTION

class WishlistModel:
    @staticmethod
    def _col():
        db = Database.get_instance()
        return db[WISHLIST_COLLECTION]

    @staticmethod
    def add(user_id: str, book_id: str) -> bool:
        col = WishlistModel._col()
        doc = {
            "user_id": ObjectId(user_id),
            "book_id": str(book_id),
            "added_at": datetime.utcnow()
        }
        col.insert_one(doc)
        return True

    @staticmethod
    def remove(user_id: str, book_id: str) -> bool:
        col = WishlistModel._col()
        res = col.delete_one({
            "user_id": ObjectId(user_id),
            "book_id": str(book_id)
        })
        return res.deleted_count > 0

    @staticmethod
    def exists(user_id: str, book_id: str) -> bool:
        col = WishlistModel._col()
        return col.find_one({
            "user_id": ObjectId(user_id),
            "book_id": str(book_id)
        }) is not None

    @staticmethod
    def list_book_ids(user_id: str, limit: int = 200):
        col = WishlistModel._col()
        cursor = col.find(
            {"user_id": ObjectId(user_id)},
            {"_id": 0, "book_id": 1}
        ).sort("added_at", -1).limit(limit)

        return [x["book_id"] for x in cursor]
