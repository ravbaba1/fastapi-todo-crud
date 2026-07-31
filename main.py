from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class TaskBlueprint(BaseModel):
    title: str
    completed: bool

# Helper function to open a clean connection to our hard drive file
def get_db_connection():
    conn = sqlite3.connect("todo.db")
    # This magic line lets us fetch results as clean Python dictionaries instead of raw tuples
    conn.row_factory = sqlite3.Row
    return conn

# 1. READ ALL TASKS FROM THE DATABASE
@app.get("/tasks")
def get_all_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, completed FROM tasks")
    rows = cursor.fetchall()
    
    conn.close()
    
    # Convert database rows into a readable list of dictionaries
    return [dict(row) for row in rows]

# 2. CREATE A TASK PERMANENTLY IN THE DATABASE
@app.post("/tasks")
def create_task(new_task: TaskBlueprint):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 🛡️ Secure Parameterized Query protects against SQL Injection
    query = "INSERT INTO tasks (title, completed) VALUES (?, ?)"
    cursor.execute(query, (new_task.title, new_task.completed))
    
    # Save the changes permanently to the file
    conn.commit()
    conn.close()
    
    return {"message": "Task saved permanently to the database!"}

# 3. UPDATE A TASK IN THE DATABASE
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: TaskBlueprint):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 🛡️ Parameterized query protecting against SQLi
    query = "UPDATE tasks SET title = ?, completed = ? WHERE id = ?"
    cursor.execute(query, (updated_task.title, updated_task.completed, task_id))
    
    # Check if the row actually existed and was updated
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found to update")
        
    conn.commit()
    conn.close()
    return {"message": f"Task {task_id} updated successfully inside the database!"}

# 4. DELETE A TASK FROM THE DATABASE
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 🛡️ Parameterized query protecting against SQLi
    query = "DELETE FROM tasks WHERE id = ?"
    cursor.execute(query, (task_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found to delete")
        
    conn.commit()
    conn.close()
    return {"message": f"Task {task_id} permanently erased from the database!"}