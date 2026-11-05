from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import bcrypt
import re
from database.db import get_db
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({"error": "Authentication required"}), 401
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def validate_email(email):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email) is not None


def validate_password(password):
    return len(password) >= 8


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not validate_email(email):
            errors.append("Please enter a valid email address.")
        if not validate_password(password):
            errors.append("Password must be at least 8 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template('register.html', username=username, email=email)

        # Check uniqueness
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            flash("Username or email already registered.", "danger")
            return render_template('register.html', username=username, email=email)

        # Hash password and store
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        session['user_id'] = user_id
        session['username'] = username
        session['email'] = email
        flash(f"Welcome, {username}! Your account has been created.", "success")
        return redirect(url_for('dashboard.dashboard'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash("Please fill in all fields.", "danger")
            return render_template('login.html', email=email)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Invalid email or password.", "danger")
            return render_template('login.html', email=email)

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if validate_email(email):
            flash("If that email is registered, you'll receive a reset link shortly. (Email service not configured in demo mode)", "info")
        else:
            flash("Please enter a valid email address.", "danger")
    return render_template('forgot_password.html')
