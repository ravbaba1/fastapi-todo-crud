import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Load the secret variables from the .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Establishes a connection to the Postgres database."""
    # We add row_factory=dict_row here. This replaces the old RealDictCursor layout!
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return conn

def init_db():
    """Creates the database table automatically if it doesn't exist yet."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # NOTE: Replace 'items' and the columns below with your actual data structure
    # For example, if your CRUD app tracks 'users', change this to match your old setup!
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database table initialized successfully!")
