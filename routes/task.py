from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from pydantic import BaseModel
from datetime import date

router = APIRouter()


# ================= DB =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= Schemas =================
class TaskCreate(BaseModel):
    title: str
    assigned_to: int
    project_id: int
    due_date: date
    creator_id: int   #  who is creating (admin)


class TaskUpdate(BaseModel):
    status: str
    user_id: int   #  who is updating


# ================= CREATE TASK =================
@router.post("/create_task")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):

    #  creator must be admin
    creator = db.query(models.User).filter(models.User.id == task.creator_id).first()
    if not creator or creator.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create tasks")

    # check assigned user exists
    user = db.query(models.User).filter(models.User.id == task.assigned_to).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # check project exists
    project = db.query(models.Project).filter(models.Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    #  check user is part of project
    member = db.query(models.ProjectMember).filter(
        models.ProjectMember.user_id == task.assigned_to,
        models.ProjectMember.project_id == task.project_id
    ).first()

    if not member:
        raise HTTPException(status_code=403, detail="User is not part of this project")

    new_task = models.Task(
        title=task.title,
        assigned_to=task.assigned_to,
        project_id=task.project_id,
        due_date=task.due_date,
        status="pending"
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {"message": "Task created", "task_id": new_task.id}


# ================= UPDATE TASK =================
@router.put("/update_task/{task_id}")
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):

    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    #  Only assigned user OR admin can update
    if user.role != "admin" and task.assigned_to != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    #  status validation
    if data.status not in ["pending", "in-progress", "done"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    task.status = data.status
    db.commit()

    return {"message": "Task updated"}


# ================= GET ALL TASKS =================
@router.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()


# ================= DASHBOARD =================
@router.get("/dashboard/{user_id}")
def dashboard(user_id: int, project_id: int = None, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == user_id).first()

    query = db.query(models.Task)

    if user.role != "admin":
        query = query.filter(models.Task.assigned_to == user_id)

    if project_id:
        query = query.filter(models.Task.project_id == project_id)

    tasks = query.all()

    from datetime import date
    today = date.today()

    result = []
    for t in tasks:
        overdue = False
        if t.due_date and t.due_date < today and t.status != "done":
            overdue = True

        result.append({
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "due_date": t.due_date,
            "overdue": overdue
        })

    return {"tasks": result}