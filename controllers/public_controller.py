from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user
from models.category_model import CategoryModel
from models.author_model import AuthorModel
from models.message_model import MessageModel
from models.history_model import HistoryModel
from services.search_service import SBERTSearchService
from bson.objectid import ObjectId

public_bp = Blueprint('public_bp', __name__)
search_engine = SBERTSearchService()

@public_bp.route('/')
def home():
    return render_template('index.html')

@public_bp.route('/category')
def category():
    all_categories = CategoryModel.get_all_categories()
    return render_template('categories.html', categories=all_categories)

@public_bp.route('/category/<category_id>')
def view_category_books(category_id):
    category = CategoryModel.get_category_by_id(category_id)
    if not category:
        flash("Category not found.", "warning")
        return redirect(url_for('public_bp.category'))
        
    books_in_category = [book for book in search_engine.books if str(category_id) in book.get("category_ids", [])]
    return render_template('category_books.html', category=category, books=books_in_category)

@public_bp.route('/all_author')
def author():
    all_authors = AuthorModel.get_all_authors()
    return render_template('All_authors.html', authors=all_authors)

@public_bp.route('/author/<author_name>')
def author_profile(author_name):
    author = AuthorModel.get_author_by_name(author_name)
    if not author:
        flash("Author not found.", "warning")
        return redirect(url_for('public_bp.home'))
        
    author_id_str = str(author['_id'])
    author_books = [book for book in search_engine.books if author_id_str in book.get("author_ids", [])]
    return render_template('author.html', author=author, books=author_books)

@public_bp.route('/book/<book_id>')
def show_book_page(book_id):
    return render_template('book_info.html', book_id=book_id)

@public_bp.route('/read/<book_id>')
def read_book(book_id):
    book = search_engine.get_book_by_id(book_id)
    if not book or 'pdf_file' not in book or not book['pdf_file']:
        flash("Sorry, the PDF for this book is not available.", "warning")
        return redirect(url_for('public_bp.show_book_page', book_id=book_id))
        
    if current_user.is_authenticated:
        HistoryModel.save_history(current_user.id, book_id)
        
    pdf_url = f"/static/uploads/books/pdfs/{book['pdf_file']}"
    book_title = book.get('title', 'Read Book')
    return render_template('read-book.html', pdf_url=pdf_url, book_title=book_title)

@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if name and email and message:
            MessageModel.add_message(name, email, subject, message)
            flash("Your message has been sent successfully!", "success")
            return redirect(url_for('public_bp.contact'))
        else:
            flash("Please fill out all required fields.", "error")

    return render_template('contact.html')

@public_bp.route('/api/popular-books', methods=['GET'])
def get_popular_books():
    popular_data = HistoryModel.get_most_read_books(12)
    popular_books = []
    
    for item in popular_data:
        book = search_engine.get_book_by_id(item['_id'])
        if book:
            popular_books.append(book)
            
    if len(popular_books) < 12:
        for eb in search_engine.books:
            if not any(pb.get('id') == str(eb.get('_id', '')) for pb in popular_books):
                popular_books.append(search_engine._format_book_for_frontend(eb))
            if len(popular_books) == 12:
                break
                
    return jsonify({"books": popular_books})

@public_bp.route('/api/popular-categories', methods=['GET'])
def get_popular_categories():
    all_cats = CategoryModel.get_all_categories()
    popular_categories = []
    for c in all_cats[:8]:
        c['_id'] = str(c['_id'])
        popular_categories.append(c)
    return jsonify({"categories": popular_categories})