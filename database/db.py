import sqlite3
import os
from config import Config

def create_schema(conn):
    """Create database tables if they do not exist."""
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            avatar_url TEXT DEFAULT NULL,
            bio TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Captions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS captions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            category TEXT NOT NULL,
            tone TEXT NOT NULL,
            topic TEXT NOT NULL,
            caption_text TEXT NOT NULL,
            hashtags TEXT,
            keywords TEXT,
            caption_length TEXT DEFAULT 'medium',
            is_saved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Favorites table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            caption_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (caption_id) REFERENCES captions(id) ON DELETE CASCADE,
            UNIQUE(user_id, caption_id)
        )
    ''')

    conn.commit()


def get_db():
    """Get a database connection, auto-initializing schema if needed."""
    db_path = Config.DATABASE_PATH
    db_dir = os.path.dirname(db_path)
    if db_dir:
        try:
            os.makedirs(db_dir, exist_ok=True)
        except OSError:
            pass
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # Ensure tables exist
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        create_schema(conn)

    return conn

def init_db():
    """Initialize the database with schema."""
    conn = get_db()
    create_schema(conn)
    conn.close()
    print("[OK] Database initialized successfully.")
