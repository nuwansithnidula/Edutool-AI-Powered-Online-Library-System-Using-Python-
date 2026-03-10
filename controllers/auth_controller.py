import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message

# MVC ආකෘතියට අනුව Models සහ Utils භාවිතා කිරීම
from extensions import mail 
from utils.bd import Database
from models.user_model import User
from models.message_model import MessageModel

auth_bp = Blueprint('auth_bp', __name__)

# --- Admin Dashboard Route ---
@auth_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # If a non-admin visits this page, they will be redirected to the home page.
    if current_user.role != 'admin':
        return redirect(url_for('public_bp.home'))

    active_tab = request.args.get('tab', 'dashboard')
    
    # Database instance (Singleton pattern)
    db = Database.get_instance()
    
    all_authors = list(db['authors'].find().sort("created_at", -1))
    all_categories = list(db['category'].find().sort("created_at", -1))
    all_drafts = list(db['draft_books'].find().sort("created_at", -1))
    all_users = list(db['users'].find().sort("_id", -1))
    all_books = list(db['books'].find().sort("created_at", -1))
    
    # Retrieving data using the Message Model
    messages = MessageModel.get_all_messages()
    unread_count = MessageModel.get_unread_count()
    
    counts = {
        'books': db['books'].count_documents({}),
        'authors': db['authors'].count_documents({}),
        'categories': db['category'].count_documents({}),
        'users': db['users'].count_documents({})
    }
    
    return render_template('admin/admin_dashboard.html', 
                           authors=all_authors, 
                           categories=all_categories,
                           drafts=all_drafts,
                           users=all_users,
                           books=all_books,  
                           counts=counts,
                           messages=messages, 
                           unread_count=unread_count,
                           active_tab=active_tab)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('auth_bp.admin_dashboard'))
        return redirect(url_for('public_bp.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.get_by_email(email)
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            if user.role == 'admin':
                return redirect(url_for('auth_bp.admin_dashboard'))
            return redirect(url_for('public_bp.home'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('public_bp.home'))

    if request.method == 'POST':
        fname = request.form.get('first_name')
        lname = request.form.get('last_name')
        dob = request.form.get('dob')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.create_user(fname, lname, dob, email, password, role='user'):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth_bp.login'))
        else:
            flash('Email already exists.', 'danger')

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('public_bp.home'))

# --- Forgot Password & OTP Logic ---
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.get_by_email(email)

        if user:
            otp_code = str(random.randint(100000, 999999))
            User.set_otp(email, otp_code)

            try:
                msg = Message('LibroJet Password Reset OTP', 
                              sender='noreply@librojet.com', 
                              recipients=[email])
                msg.body = f"Your OTP code is: {otp_code}\n\nThis code expires in 1 minute."
                mail.send(msg)
                
                session['reset_email'] = email
                flash('OTP sent to your email!', 'info')
                return redirect(url_for('auth_bp.reset_password_page'))
            
            except Exception as e:
                print(f"Mail Error: {e}")
                flash('Error sending email. Check internet connection.', 'danger')
        else:
            flash('Email not found.', 'danger')
            
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password-verify', methods=['GET', 'POST'])
def reset_password_page():
    if 'reset_email' not in session:
        return redirect(url_for('auth_bp.forgot_password'))

    if request.method == 'POST':
        otp_input = request.form.get('otp')
        new_password = request.form.get('new_password')
        email = session['reset_email']

        is_valid, message = User.verify_otp(email, otp_input)

        if is_valid:
            User.reset_password_with_otp(email, new_password)
            session.pop('reset_email', None) 
            flash('Password reset successful! Please login.', 'success')
            return redirect(url_for('auth_bp.login'))
        else:
            flash(message, 'danger')

    return render_template('reset_password_otp.html')