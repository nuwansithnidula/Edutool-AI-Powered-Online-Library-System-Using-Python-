from flask import Blueprint, render_template, request, jsonify
from config import MONGO_URI
from factories.search_factory import SearchFactory
from services.ocr_service import OCRService
from flask_login import current_user
from models.interaction_model import InteractionModel
from bson import ObjectId
from flask import render_template


book_bp = Blueprint('book_bp', __name__)
search_service = SearchFactory.get_search_service("sbert")
ocr_service = OCRService()

@book_bp.route('/search', methods=['POST'])
def search():
    """
    NLP Search, OCR Search
    """
    text_query = request.form.get('query', '')

    image_file = request.files.get('image')
    extracted_text = ""

    if image_file:
        print("📸 Image detected! Processing OCR...")
        extracted_text = ocr_service.extract_text_from_image(image_file)
        print(f"📝 Extracted Text: {extracted_text}")

    final_query = f"{text_query} {extracted_text}".strip()

    if not final_query:
        return jsonify({"error": "Please provide text or an image to search."}), 400

    print(f"🔎 Final Search Query to AI: '{final_query}'")

    # 5. SBERT AI search
    results = search_service.search(final_query)

    # 6. Save user interaction
    if current_user.is_authenticated:
        InteractionModel.save_search(current_user.id, final_query)

    return jsonify({
        "results": results,
        "ocr_text": extracted_text
    })


@book_bp.route('/suggest', methods=['POST'])
def suggest_books():
    data = request.json
    book_title = data.get('title', '')

    if not book_title:
        return jsonify({"error": "Book title is required"}), 400

    suggestions = search_service.get_recommendations(book_title)
    return jsonify({"suggestions": suggestions})


@book_bp.route('/picked-for-you', methods=['GET'])
def picked_for_you():
    if not current_user.is_authenticated:
        return jsonify({"picked": []})

    queries = InteractionModel.get_user_search_queries(
        user_id=current_user.id,
        limit=15
    )

    picked_books = search_service.picked_for_you(queries)
    return jsonify({"picked": picked_books})


@book_bp.route('/<book_id>', methods=['GET'])
def get_book_json(book_id):
    book = search_service.get_book_by_id(book_id)

    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    cleaned_book = {
        'id': book.get('id'),
        'title': book.get('title'),
        'authors': book.get('authors'),
        'thumbnail': book.get('thumbnail'),
        'description': book.get('description', 'No description available.'),
        'isbn': book.get('isbn', 'N/A'),
        'price': book.get('price', 0),
        'categories': book.get('categories', []),
        
        'pdf_file': book.get('pdf_file', None)

    }

    return jsonify(cleaned_book)
