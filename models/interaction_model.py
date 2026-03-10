from datetime import datetime
from utils.bd import Database
from config import INTERACTION_COLLECTION

class InteractionModel:
    """
    Handles user search interactions
    """

    @staticmethod
    def save_search(user_id, query):
        """
        Save a search query made by a logged-in user
        """
        db = Database.get_instance()

        interaction = {
            "user_id": str(user_id),  # store as STRING
            "query": query,
            "created_at": datetime.utcnow()
        }

        db[INTERACTION_COLLECTION].insert_one(interaction)

    @staticmethod
    def get_user_search_queries(user_id, limit=20):
        """
        Get recent search queries of a user
        """
        db = Database.get_instance()

        interactions = db[INTERACTION_COLLECTION].find(
            {"user_id": str(user_id)}  # match string
        ).sort("created_at", -1).limit(limit)

        return [i["query"] for i in interactions]
