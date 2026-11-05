from flask import Blueprint, render_template, request, session, jsonify, flash, redirect, url_for
from routes.auth import login_required
from services.caption_service import get_dashboard_stats
from database.db import get_db
import bcrypt

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    stats = get_dashboard_stats(session['user_id'])
    return render_template('dashboard.html', stats=stats)


@dashboard_bp.route('/profile')
@login_required
def profile():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = dict(cursor.fetchone())
    conn.close()
    return render_template('profile.html', user=user)


@dashboard_bp.route('/settings')
@login_required
def settings():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = dict(cursor.fetchone())
    conn.close()
    return render_template('settings.html', user=user)


@dashboard_bp.route('/api/profile', methods=['POST'])
@login_required
def api_update_profile():
    data = request.get_json()
    username = data.get('username', '').strip()
    bio = data.get('bio', '').strip()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()

    # Update username/bio
    if username and username != user['username']:
        cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?",
                       (username, session['user_id']))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "Username already taken"}), 400
        cursor.execute("UPDATE users SET username = ? WHERE id = ?",
                       (username, session['user_id']))
        session['username'] = username

    if bio is not None:
        cursor.execute("UPDATE users SET bio = ? WHERE id = ?", (bio, session['user_id']))

    # Update password
    if current_password and new_password:
        if not bcrypt.checkpw(current_password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            conn.close()
            return jsonify({"error": "Current password is incorrect"}), 400
        if len(new_password) < 8:
            conn.close()
            return jsonify({"error": "New password must be at least 8 characters"}), 400
        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                       (new_hash, session['user_id']))

    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Profile updated successfully"})


@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    stats = get_dashboard_stats(session['user_id'])
    return jsonify({"success": True, "stats": stats})
