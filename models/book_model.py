from utils.bd import Database
from config import COLLECTION_NAME
from bson.objectid import ObjectId 

class BookModel:
    def __init__(self):
        self.db = Database.get_instance()
        self.collection = self.db[COLLECTION_NAME] # books collection
        
        self.authors_collection = self.db['authors'] 
        self.categories_collection = self.db['category']

    def get_all_books(self):
        """Getting all the books"""
        books = list(self.collection.find({})) 
        return books

    def add_book(self, book_data):
        """Adding a new book to the database"""
        return self.collection.insert_one(book_data)


    def get_author_names_by_ids(self, author_ids):
        """Given a list of IDs, get the names of the relevant authors"""
        if not author_ids:
            return []

        object_ids = []
        for aid in author_ids:
            try:
                object_ids.append(ObjectId(aid) if isinstance(aid, str) else aid)
            except Exception:
                pass 
                
        authors = list(self.authors_collection.find({"_id": {"$in": object_ids}}))
        return [author.get('name', '') for author in authors]

    def get_category_names_by_ids(self, category_ids):
        """Given a list of IDs, get the names of the relevant categories"""
        if not category_ids:
            return []
            
        object_ids = []
        for cid in category_ids:
             try:
                 object_ids.append(ObjectId(cid) if isinstance(cid, str) else cid)
             except Exception:
                 pass
                 
        categories = list(self.categories_collection.find({"_id": {"$in": object_ids}}))
        return [category.get('name', '') for category in categories]