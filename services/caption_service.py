from database.db import get_db
import json

def save_caption(user_id, platform, category, tone, topic, caption_text, hashtags, keywords="", caption_length="medium", is_saved=0):
    """Save a generated caption to the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO captions (user_id, platform, category, tone, topic, caption_text, hashtags, keywords, caption_length, is_saved)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, platform, category, tone, topic, caption_text, hashtags, keywords, caption_length, is_saved))
    conn.commit()
    caption_id = cursor.lastrowid
    conn.close()
    return caption_id


def get_user_captions(user_id, is_saved=None, platform=None, category=None, search=None, limit=50, offset=0):
    """Get captions for a user with optional filters."""
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT c.*, (SELECT COUNT(*) FROM favorites f WHERE f.caption_id = c.id AND f.user_id = ?) as is_favorite FROM captions c WHERE c.user_id = ?"
    params = [user_id, user_id]

    if is_saved is not None:
        query += " AND c.is_saved = ?"
        params.append(is_saved)
    if platform:
        query += " AND c.platform = ?"
        params.append(platform)
    if category:
        query += " AND c.category = ?"
        params.append(category)
    if search:
        query += " AND (c.caption_text LIKE ? OR c.topic LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY c.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_caption_by_id(caption_id, user_id):
    """Get a single caption belonging to user."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM captions WHERE id = ? AND user_id = ?", (caption_id, user_id))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_caption(caption_id, user_id, caption_text=None, is_saved=None):
    """Update a caption."""
    conn = get_db()
    cursor = conn.cursor()
    if caption_text is not None:
        cursor.execute("UPDATE captions SET caption_text = ? WHERE id = ? AND user_id = ?",
                       (caption_text, caption_id, user_id))
    if is_saved is not None:
        cursor.execute("UPDATE captions SET is_saved = ? WHERE id = ? AND user_id = ?",
                       (is_saved, caption_id, user_id))
    conn.commit()
    conn.close()


def delete_caption(caption_id, user_id):
    """Delete a caption."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM captions WHERE id = ? AND user_id = ?", (caption_id, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def toggle_favorite(user_id, caption_id):
    """Toggle a caption as favorite. Returns True if added, False if removed."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM favorites WHERE user_id = ? AND caption_id = ?", (user_id, caption_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("DELETE FROM favorites WHERE user_id = ? AND caption_id = ?", (user_id, caption_id))
        added = False
    else:
        cursor.execute("INSERT INTO favorites (user_id, caption_id) VALUES (?, ?)", (user_id, caption_id))
        added = True

    conn.commit()
    conn.close()
    return added


def get_favorites(user_id):
    """Get user's favorite captions."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, 1 as is_favorite FROM captions c
        INNER JOIN favorites f ON c.id = f.caption_id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_dashboard_stats(user_id):
    """Get dashboard statistics for a user."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM captions WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as saved FROM captions WHERE user_id = ? AND is_saved = 1", (user_id,))
    saved = cursor.fetchone()['saved']

    cursor.execute("SELECT COUNT(*) as favs FROM favorites WHERE user_id = ?", (user_id,))
    favs = cursor.fetchone()['favs']

    # Platform breakdown
    cursor.execute('''
        SELECT platform, COUNT(*) as count FROM captions
        WHERE user_id = ? GROUP BY platform ORDER BY count DESC
    ''', (user_id,))
    platforms = [dict(row) for row in cursor.fetchall()]

    # Recent captions (last 5)
    cursor.execute('''
        SELECT * FROM captions WHERE user_id = ? ORDER BY created_at DESC LIMIT 5
    ''', (user_id,))
    recent = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return {
        "total_generated": total,
        "saved_captions": saved,
        "favorites": favs,
        "platform_stats": platforms,
        "recent_captions": recent
    }
