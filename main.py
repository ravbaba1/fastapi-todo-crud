from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# 1. Define a strict blueprint for what a Task MUST look like
class TaskBlueprint(BaseModel):
    id: int
    title: str
    completed: bool

todo_db = [
    {"id": 1, "title": "Setup Python environment", "completed": True},
    {"id": 2, "title": "Build Stage 0 server", "completed": True},
    {"id": 3, "title": "Learn how to read tasks", "completed": False}
]

@app.get("/tasks")
def get_all_tasks():
    return todo_db

# 2. Force the POST route to use our strict blueprint
@app.post("/tasks")
def create_task(new_task: TaskBlueprint):
    # Convert the secure blueprint back into a regular Python format to append it
    todo_db.append(new_task.model_dump())
    return {"message": "Task added successfully!", "current_database": todo_db}

# 1. UPDATE Route (Modifies a task if it exists)
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: TaskBlueprint):
    for item in todo_db:
        if item["id"] == task_id:
            item["title"] = updated_task.title
            item["completed"] = updated_task.completed
            return {"message": "Task updated successfully", "updated_item": item}
    raise HTTPException(status_code=404, detail="Task not found to update")

# 2. DELETE Route (Removes a task from our list)
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for item in todo_db:
        if item["id"] == task_id:
            todo_db.remove(item)
            return {"message": f"Task {task_id} deleted successfully", "current_database": todo_db}
    raise HTTPException(status_code=404, detail="Task not found to delete")