from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from models.wishlist_model import WishlistModel
from factories.search_factory import SearchFactory

wishlist_bp = Blueprint("wishlist_bp", __name__)

# Getting the Search Service
search_service = SearchFactory.get_search_service("sbert")

@wishlist_bp.route("/api/wishlist", methods=["GET"])
@login_required
def get_wishlist():
    try:
        #Get the user's book ID list
        book_ids = WishlistModel.list_book_ids(current_user.id)

        books = []
        for bid in book_ids:
            # Getting book details through the Search Service
            b = search_service.get_book_by_id(bid)
            if not b:
                continue

            books.append({
                "id": b.get("id") or str(b.get("_id")),
                "title": b.get("title"),
                "authors": b.get("authors"),
                "thumbnail": b.get("thumbnail"),
                "description": b.get("description", ""),
                "isbn": b.get("isbn", "N/A"),
                "price": b.get("price", 0)
            })

        return jsonify({"books": books})
    except Exception as e:
        print(f"Error fetching wishlist: {e}")
        return jsonify({"books": [], "error": str(e)}), 500

@wishlist_bp.route("/api/wishlist/toggle", methods=["POST"])
@login_required
def toggle_wishlist():
    try:
        data = request.get_json(force=True)
        book_id = data.get("book_id")

        if not book_id:
            return jsonify({"error": "book_id is required"}), 400

        # Check if it is already in the Wishlist
        if WishlistModel.exists(current_user.id, book_id):
            # Remove that data from the collection.
            deleted = WishlistModel.remove(current_user.id, book_id)
            if deleted:
                return jsonify({"action": "removed", "in_wishlist": False})
            else:
                return jsonify({"error": "Failed to remove from database"}), 500
        
        # New entry
        WishlistModel.add(current_user.id, book_id)
        return jsonify({"action": "added", "in_wishlist": True})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@wishlist_bp.route("/api/wishlist/contains/<book_id>", methods=["GET"])
@login_required
def contains(book_id):
    in_list = WishlistModel.exists(current_user.id, book_id)
    return jsonify({"book_id": book_id, "in_wishlist": in_list})