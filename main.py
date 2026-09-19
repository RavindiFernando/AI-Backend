from fastapi import FastAPI, HTTPException

app = FastAPI()

# In-memory "database"
tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Read chapter 3", "done": False},
    {"id": 3, "title": "Submit assignment", "done": True},
]

@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def list_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")