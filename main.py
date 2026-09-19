from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Task API", version="1.0")

# In-memory "database"
DEFAULT_TASKS = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Read chapter 3", "done": False},
    {"id": 3, "title": "Submit assignment", "done": True},
]
tasks = [t.copy() for t in DEFAULT_TASKS]
next_id = 4


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/", summary="API info")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List tasks, optionally filtered by done status or search term")
def list_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    result = tasks

    if done is not None:
        result = [t for t in result if t["done"] == done]

    if search is not None:
        result = [t for t in result if search.lower() in t["title"].lower()]

    return result


@app.get("/tasks/{task_id}", summary="Get a single task by id")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.get("/stats", summary="Get task counts")
def get_stats():
    total = len(tasks)
    done_count = len([t for t in tasks if t["done"]])
    return {"total": total, "done": done_count, "open": total - done_count}


@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task: TaskCreate):
    global next_id
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")

    new_task = {"id": next_id, "title": task.title, "done": False}
    tasks.append(new_task)
    next_id += 1
    return new_task


@app.put("/tasks/{task_id}", summary="Update a task's title and/or done status")
def update_task(task_id: int, update: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            if update.title is not None:
                if not update.title.strip():
                    raise HTTPException(status_code=400, detail="title cannot be empty")
                task["title"] = update.title
            if update.done is not None:
                task["done"] = update.done
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.post("/reset", summary="Reset tasks back to the default seed data")
def reset_tasks():
    global tasks, next_id
    tasks = [t.copy() for t in DEFAULT_TASKS]
    next_id = 4
    return {"message": "Tasks reset to default", "tasks": tasks}