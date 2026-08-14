import os
import sqlite3
from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, status
from receipt_router import router as receipt_router
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client
from database import init_db, get_db_connection

# Load secrets from the environment
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError("Security Alert: Missing Supabase environment keys!")

# Create connection client to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

app = FastAPI(title="Flyrank Secure To-Do API")
app.include_router(receipt_router)

# Setup database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Security scheme for Swagger UI lock icons
security_scheme = HTTPBearer()

# --- MODEL BLUEPRINTS ---
class TaskBlueprint(BaseModel):
    title: str
    completed: bool

class UserAuthSchema(BaseModel):
    email: str
    password: str

# --- AUTHENTICATION DEPENDENCY ---
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)]
) -> dict:
    try:
        token = credentials.credentials
        user_response = supabase.auth.get_user(token)
        user_data = user_response.user
        
        if not user_data:
            raise HTTPException(status_code=401, detail="Session invalid or expired.")
            
        return {"id": user_data.id, "email": user_data.email}
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed. Invalid token.")

# --- AUTHENTICATION ROUTES ---
@app.post("/auth/signup", tags=["Authentication"])
def sign_up(user_credentials: UserAuthSchema):
    try:
        response = supabase.auth.sign_up({
            "email": user_credentials.email,
            "password": user_credentials.password
        })
        return {"message": "Registration successful! Check your inbox to confirm.", "user_id": response.user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", tags=["Authentication"])
def log_in(user_credentials: UserAuthSchema):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user_credentials.email,
            "password": user_credentials.password
        })
        return {"access_token": response.session.access_token, "user_id": response.user.id, "email": response.user.email}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

# ==========================================
#          SECURED PROTECTED CRUD 
# ==========================================

@app.get("/tasks", tags=["Protected CRUD"])
def get_all_tasks(current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description FROM items WHERE user_id = ?", (current_user["id"],))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"GET Error: {str(e)}")

@app.post("/tasks", tags=["Protected CRUD"])
def create_task(new_task: TaskBlueprint, current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO items (user_id, title, description) VALUES (?, ?, ?)"
        status_text = "Completed" if new_task.completed else "Pending"
        cursor.execute(query, (current_user["id"], new_task.title, f"Status: {status_text}"))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Task saved permanently and isolated to your account!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"POST Error: {str(e)}")

@app.put("/tasks/{task_id}", tags=["Protected CRUD"])
def update_task(task_id: int, updated_task: TaskBlueprint, current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "UPDATE items SET title = ?, description = ? WHERE id = ? AND user_id = ?"
        status_text = "Completed" if updated_task.completed else "Pending"
        cursor.execute(query, (updated_task.title, f"Status: {status_text}", task_id, current_user["id"]))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=44, detail="Item not found or unauthorized modification attempt.")
            
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": f"Task {task_id} updated successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PUT Error: {str(e)}")

@app.delete("/tasks/{task_id}", tags=["Protected CRUD"])
def delete_task(task_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "DELETE FROM items WHERE id = ? AND user_id = ?"
        cursor.execute(query, (task_id, current_user["id"]))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Item not found or unauthorized deletion attempt.")
            
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": f"Task {task_id} permanently erased!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"DELETE Error: {str(e)}")
