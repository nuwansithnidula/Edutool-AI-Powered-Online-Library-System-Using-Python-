from utils.bd import Database
from bson.objectid import ObjectId
from datetime import datetime

class CommentModel:
    @staticmethod
    def _col():
        db = Database.get_instance()
        return db['comments']

    @staticmethod
    def get_comments_by_book(book_id):
        comments = list(CommentModel._col().find({"book_id": str(book_id)}).sort("created_at", -1))
        for c in comments:
            c['_id'] = str(c['_id'])
            c['created_at'] = c['created_at'].strftime("%Y-%m-%d %H:%M") if 'created_at' in c else "Just now"
        return comments

    @staticmethod
    def add_comment(book_id, user_id, user_name, user_image, text):
        comment = {
            "book_id": str(book_id),
            "user_id": str(user_id),
            "user_name": user_name,
            "user_image": user_image,
            "text": text,
            "created_at": datetime.now()
        }
        return CommentModel._col().insert_one(comment)

    @staticmethod
    def get_comment_by_id(comment_id):
        return CommentModel._col().find_one({"_id": ObjectId(comment_id)})

    @staticmethod
    def update_comment(comment_id, text):
        return CommentModel._col().update_one({"_id": ObjectId(comment_id)}, {"$set": {"text": text}})

    @staticmethod
    def delete_comment(comment_id):
        return CommentModel._col().delete_one({"_id": ObjectId(comment_id)})