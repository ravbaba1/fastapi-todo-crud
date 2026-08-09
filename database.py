import sqlite3

def get_db_connection():
    """Establishes a connection to the local SQLite database file."""
    conn = sqlite3.connect("todo.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates the local SQLite items table automatically if it doesn't exist yet."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # We build the 'items' table with the exact columns your endpoints require
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database table 'items' initialized successfully with anti-IDOR defense columns!")