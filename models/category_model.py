from utils.bd import Database
from bson.objectid import ObjectId
from datetime import datetime

class CategoryModel:
    @staticmethod
    def _col():
        db = Database.get_instance()
        return db['category']

    @staticmethod
    def get_all_categories():
        return list(CategoryModel._col().find().sort("name", 1))

    @staticmethod
    def get_all_categories_desc():
        return list(CategoryModel._col().find().sort("created_at", -1))

    @staticmethod
    def get_category_by_id(category_id):
        try:
            return CategoryModel._col().find_one({"_id": ObjectId(category_id)})
        except Exception:
            return None

    @staticmethod
    def check_duplicate(name):
        return CategoryModel._col().find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})

    @staticmethod
    def add_category(name, icon_class):
        category_data = {
            "name": name,
            "icon": icon_class,
            "created_at": datetime.now()
        }
        return CategoryModel._col().insert_one(category_data)

    @staticmethod
    def update_category(category_id, update_data):
        return CategoryModel._col().update_one(
            {'_id': ObjectId(category_id)}, 
            {'$set': update_data}
        )

    @staticmethod
    def delete_category(category_id):
        return CategoryModel._col().delete_one({'_id': ObjectId(category_id)})

    @staticmethod
    def get_popular_categories(limit=8):
        pass