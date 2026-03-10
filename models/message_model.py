from utils.bd import Database
from bson.objectid import ObjectId
from datetime import datetime

class MessageModel:
    @staticmethod
    def _col():
        db = Database.get_instance()
        return db['messages']

    @staticmethod
    def add_message(name, email, subject, message):
        msg_data = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "is_read": False,
            "created_at": datetime.now()
        }
        return MessageModel._col().insert_one(msg_data)

    @staticmethod
    def get_all_messages():
        return list(MessageModel._col().find().sort("created_at", -1))

    @staticmethod
    def get_unread_count():
        return MessageModel._col().count_documents({"is_read": {"$ne": True}})

    @staticmethod
    def mark_as_read(message_id):
        return MessageModel._col().update_one({'_id': ObjectId(message_id)}, {'$set': {'is_read': True}})

    @staticmethod
    def mark_all_as_read():
        return MessageModel._col().update_many({"is_read": {"$ne": True}}, {"$set": {"is_read": True}})

    @staticmethod
    def delete_message(message_id):
        return MessageModel._col().delete_one({'_id': ObjectId(message_id)})