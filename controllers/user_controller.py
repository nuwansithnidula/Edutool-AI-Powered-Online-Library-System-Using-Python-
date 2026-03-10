import os
import time
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.history_model import HistoryModel
from models.comment_model import CommentModel
from models.user_model import User
from utils.bd import Database
from services.search_service import SBERTSearchService

user_bp = Blueprint('user_bp', __name__)
search_engine = SBERTSearchService()

@user_bp.route('/view_profile')
@login_required
def view_profile():
    return render_template('profile.html')

@user_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    user_email = current_user.email
    db = Database.get_instance()
    
    fname = request.form.get('first_name')
    lname = request.form.get('last_name')
    dob = request.form.get('birthday')
    
    update_data = {}
    if fname: update_data['fname'] = fname
    if lname: update_data['lname'] = lname
    if dob: update_data['dob'] = dob

    new_image_url = None

    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file.filename != '':
            filename = secure_filename(f"{user_email}_{file.filename}")
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            db_image_path = f"/static/uploads/profiles/{filename}"
            update_data['profile_image'] = db_image_path
            new_image_url = f"{db_image_path}?t={int(time.time())}"

    if update_data:
        db['users'].update_one({'email': user_email}, {'$set': update_data})

    return jsonify({
        'success': True,
        'message': 'Profile updated successfully!',
        'new_image_url': new_image_url
    })

@user_bp.route('/api/history', methods=['GET'])
@login_required
def get_user_history():
    user_history = HistoryModel.get_user_history(current_user.id)
    history_books = []
    for item in user_history:
        book = search_engine.get_book_by_id(item['book_id'])
        if book:
            history_books.append(book)
    return jsonify({"books": history_books})

@user_bp.route('/api/history/remove', methods=['POST'])
@login_required
def remove_from_history():
    book_id = request.json.get('book_id')
    if not book_id:
        return jsonify({"success": False, "error": "Book ID is required"}), 400
        
    result = HistoryModel.remove_from_history(current_user.id, book_id)
    if result.deleted_count > 0:
        return jsonify({"success": True, "message": "Removed from history"})
    return jsonify({"success": False, "error": "Record not found"}), 404

# --- Comments API Routes ---
@user_bp.route('/api/comments/<book_id>', methods=['GET'])
def get_comments(book_id):
    comments = CommentModel.get_comments_by_book(book_id)
    return jsonify({"comments": comments})

@user_bp.route('/api/comments/add', methods=['POST'])
@login_required
def add_comment():
    data = request.json
    book_id = data.get('book_id')
    text = data.get('text')
    
    if not text or not book_id:
        return jsonify({"error": "Text and Book ID are required"}), 400
        
    user_name = f"{current_user.fname} {current_user.lname}"
    CommentModel.add_comment(book_id, current_user.id, user_name, current_user.profile_image, text)
    return jsonify({"success": True})

@user_bp.route('/api/comments/edit/<comment_id>', methods=['PUT'])
@login_required
def edit_comment(comment_id):
    new_text = request.json.get('text')
    comment = CommentModel.get_comment_by_id(comment_id)
    
    if not comment or comment['user_id'] != str(current_user.id):
        return jsonify({"error": "Unauthorized"}), 403
        
    CommentModel.update_comment(comment_id, new_text)
    return jsonify({"success": True})

@user_bp.route('/api/comments/delete/<comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    comment = CommentModel.get_comment_by_id(comment_id)
    if not comment or comment['user_id'] != str(current_user.id):
        return jsonify({"error": "Unauthorized"}), 403
        
    CommentModel.delete_comment(comment_id)
    return jsonify({"success": True})