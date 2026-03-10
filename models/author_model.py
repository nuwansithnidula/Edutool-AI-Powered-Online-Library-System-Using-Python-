from utils.bd import Database
from bson.objectid import ObjectId
from datetime import datetime

class AuthorModel:
    @staticmethod
    def _col():
        db = Database.get_instance()
        return db['authors']

    @staticmethod
    def get_all_authors():
        return list(AuthorModel._col().find().sort("name", 1))

    @staticmethod
    def get_all_authors_desc():
        return list(AuthorModel._col().find().sort("created_at", -1))

    @staticmethod
    def get_author_by_id(author_id):
        try:
            return AuthorModel._col().find_one({"_id": ObjectId(author_id)})
        except Exception:
            return None

    @staticmethod
    def get_author_by_name(name):
        return AuthorModel._col().find_one({"name": name})

    @staticmethod
    def check_duplicate(name):
        # "kamal" සහ "Kamal" එකක් ලෙස සලකයි (Case-insensitive)
        return AuthorModel._col().find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})

    @staticmethod
    def add_author(name, bio, image_filename):
        author_data = {
            "name": name,
            "bio": bio,
            "image": image_filename,
            "created_at": datetime.now()
        }
        return AuthorModel._col().insert_one(author_data)

    @staticmethod
    def update_author(author_id, update_data):
        return AuthorModel._col().update_one(
            {'_id': ObjectId(author_id)}, 
            {'$set': update_data}
        )

    @staticmethod
    def delete_author(author_id):
        return AuthorModel._col().delete_one({'_id': ObjectId(author_id)})