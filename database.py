import sqlite3

# This connects to a file named 'todo.db'. If it doesn't exist, it creates it!
connection = sqlite3.connect("todo.db")
cursor = connection.cursor()

# Create a permanent table to hold our tasks if it isn't there already
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT 0
)
""")

# Save the changes and close the connection safely
connection.commit()
connection.close()

print(" Database 'todo.db' initialized successfully on your Desktop!")