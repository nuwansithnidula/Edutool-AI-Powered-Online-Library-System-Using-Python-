import os
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from bson.objectid import ObjectId

from utils.bd import Database
from models.author_model import AuthorModel
from models.category_model import CategoryModel
from models.message_model import MessageModel

admin_bp = Blueprint('admin_bp', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Author Routes ---
@admin_bp.route('/add_author', methods=['POST'])
def add_author():
    name = request.form['author_name']
    bio = request.form['author_bio']

    if AuthorModel.check_duplicate(name):
        flash('This author is already included!', 'error')
        return redirect(url_for('auth_bp.admin_dashboard', tab='upload-author'))

    image_filename = 'default.png'
    if 'author_image' in request.files:
        file = request.files['author_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.now().timestamp()}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER_AUTHOR'], unique_filename))
            image_filename = unique_filename

    AuthorModel.add_author(name, bio, image_filename)
    flash('Author successfully added!', 'success')
    return redirect(url_for('auth_bp.admin_dashboard', tab='upload-author'))

@admin_bp.route('/update_author', methods=['POST'])
def update_author():
    author_id = request.form.get('author_id')
    name = request.form.get('author_name')
    bio = request.form.get('author_bio')

    update_data = {"name": name, "bio": bio}

    if 'author_image' in request.files:
        file = request.files['author_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.now().timestamp()}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER_AUTHOR'], unique_filename))
            update_data["image"] = unique_filename

    AuthorModel.update_author(author_id, update_data)
    return redirect(url_for('auth_bp.admin_dashboard', tab='upload-author'))

@admin_bp.route('/delete_author/<author_id>')
def delete_author(author_id):
    AuthorModel.delete_author(author_id)
    return redirect(url_for('auth_bp.admin_dashboard', tab='upload-author'))

# --- Category Routes ---
@admin_bp.route('/add_category', methods=['POST'])
def add_category():
    name = request.form['category_name']
    icon_class = request.form['category_icon']
    
    if CategoryModel.check_duplicate(name):
        flash('This category is already included!', 'error')
        return redirect(url_for('auth_bp.admin_dashboard', tab='upload-category'))

    CategoryModel.add_category(name, icon_class)
    flash('Category successfully added!', 'success')
    return redirect(url_for('auth_bp.admin_dashboard', tab='upload-category'))

@admin_bp.route('/update_category', methods=['POST'])
def update_category():
    cat_id = request.form.get('category_id')
    name = request.form.get('category_name')
    icon_class = request.form.get('category_icon')

    CategoryModel.update_category(cat_id, {"name": name, "icon": icon_class})
    return redirect(url_for('auth_bp.admin_dashboard', tab='upload-category'))

@admin_bp.route('/delete_category/<category_id>')
def delete_category(category_id):
    CategoryModel.delete_category(category_id)
    return redirect(url_for('auth_bp.admin_dashboard', tab='upload-category'))

# --- Book & Draft Handling ---
@admin_bp.route('/handle_book', methods=['POST'])
def handle_book():
    db = Database.get_instance()
    book_id = request.form.get('book_id')
    action = request.form.get('action') 
    
    book_data = {
        "title": request.form.get('book_title'),
        "published_year": request.form.get('published_year'),
        "description": request.form.get('description'),
        "author_ids": [id for id in request.form.get('author_ids', '').split(',') if id],
        "category_ids": [id for id in request.form.get('category_ids', '').split(',') if id],
        "updated_at": datetime.now()
    }

    if 'book_cover' in request.files:
        file = request.files['book_cover']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{datetime.now().timestamp()}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER_BOOKS_COVERS'], unique_name))
            book_data["cover_image"] = unique_name

    if 'book_pdf' in request.files:
        pdf_file = request.files['book_pdf']
        if pdf_file and pdf_file.filename.endswith('.pdf'):
            pdf_filename = secure_filename(pdf_file.filename)
            unique_pdf_name = f"{datetime.now().timestamp()}_{pdf_filename}"
            pdf_file.save(os.path.join(current_app.config['UPLOAD_FOLDER_BOOKS_PDFS'], unique_pdf_name))
            book_data["pdf_file"] = unique_pdf_name

    if action == 'draft':
        if book_id:
            # පබ්ලිෂ් කර ඇති පොතක්ද යන්න පරීක්ෂා කිරීම
            existing_published_book = db['books'].find_one({'_id': ObjectId(book_id)})
            if existing_published_book:
                # පබ්ලිෂ් කර ඇති පොත නැවත Draft එකක් බවට පත් කිරීම
                book_data["created_at"] = datetime.now()
                db['draft_books'].insert_one(book_data)
                db['books'].delete_one({'_id': ObjectId(book_id)})
                flash("Book successfully moved to drafts!", "success")
            else:
                # දැනටමත් Draft එකක් නම් එය Update කිරීම
                db['draft_books'].update_one({'_id': ObjectId(book_id)}, {'$set': book_data})
                flash("Draft updated successfully!", "success")
        else:
            # අලුත් Draft එකක් සේව් කිරීම
            book_data["created_at"] = datetime.now()
            db['draft_books'].insert_one(book_data)
            flash("Draft saved successfully!", "success")

    elif action == 'save':
        if book_id:
            existing_draft = db['draft_books'].find_one({'_id': ObjectId(book_id)})
            if existing_draft:
                book_data["created_at"] = datetime.now()
                db['books'].insert_one(book_data)
                db['draft_books'].delete_one({'_id': ObjectId(book_id)})
                flash("Draft successfully published as a book!", "success")
            else:
                db['books'].update_one({'_id': ObjectId(book_id)}, {'$set': book_data})
                flash("Book successfully updated!", "success")
        else:
            book_data["created_at"] = datetime.now()
            db['books'].insert_one(book_data)
            flash("Book uploaded successfully!", "success")

    return redirect(url_for('auth_bp.admin_dashboard', tab='upload-books'))


@admin_bp.route('/delete_draft/<draft_id>')
def delete_draft(draft_id):
    Database.get_instance()['draft_books'].delete_one({'_id': ObjectId(draft_id)})
    flash('Draft deleted successfully!', 'success')
    return redirect(url_for('auth_bp.admin_dashboard', tab='upload-books'))

@admin_bp.route('/delete_book/<book_id>')
def delete_book(book_id):
    Database.get_instance()['books'].delete_one({'_id': ObjectId(book_id)})
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('auth_bp.admin_dashboard', tab='dashboard'))

# --- User Management (Admin) ---
@admin_bp.route('/add_user_admin', methods=['POST'])
def add_user_admin():
    db = Database.get_instance()
    email = request.form.get('email')
    
    if db['users'].find_one({"email": email}):
        flash('This email address is already in use!', 'error')
        return redirect(url_for('auth_bp.admin_dashboard', tab='all-users'))

    image_path = '/static/uploads/profiles/default.png'
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"user_{datetime.now().timestamp()}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
            image_path = f"/static/uploads/profiles/{unique_filename}"

    user_data = {
        "fname": request.form.get('fname'),
        "lname": request.form.get('lname'),
        "dob": request.form.get('dob'),
        "email": email,
        "password": generate_password_hash(request.form.get('password')),
        "role": "user",
        "profile_image": image_path,
        "created_at": datetime.now()
    }
    
    db['users'].insert_one(user_data)
    flash('User successfully entered!', 'success')
    return redirect(url_for('auth_bp.admin_dashboard', tab='all-users'))

@admin_bp.route('/update_user_admin', methods=['POST'])
def update_user_admin():
    db = Database.get_instance()
    user_id = request.form.get('user_id')
    update_data = {
        "fname": request.form.get('fname'),
        "lname": request.form.get('lname'),
        "dob": request.form.get('dob'),
        "email": request.form.get('email')
    }

    if request.form.get('password'):
        update_data['password'] = generate_password_hash(request.form.get('password'))

    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"user_{datetime.now().timestamp()}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
            update_data["profile_image"] = f"/static/uploads/profiles/{unique_filename}"

    db['users'].update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
    flash('User successfully updated!', 'success')
    return redirect(url_for('auth_bp.admin_dashboard', tab='all-users'))

@admin_bp.route('/delete_user_admin/<user_id>')
def delete_user_admin(user_id):
    Database.get_instance()['users'].delete_one({'_id': ObjectId(user_id)})
    flash('User successfully updated!', 'success')
    return redirect(url_for('auth_bp.admin_dashboard', tab='all-users'))

# --- Message Admin Routes ---
@admin_bp.route('/api/messages/mark-read/<message_id>', methods=['POST'])
def mark_message_read(message_id):
    MessageModel.mark_as_read(message_id)
    return jsonify({"success": True})

@admin_bp.route('/api/messages/mark-all-read', methods=['POST'])
def mark_all_messages_read():
    MessageModel.mark_all_as_read()
    return jsonify({"success": True})

@admin_bp.route('/delete_message/<message_id>')
def delete_message(message_id):
    MessageModel.delete_message(message_id)
    return jsonify({"success": True})