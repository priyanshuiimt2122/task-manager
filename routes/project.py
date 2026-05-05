from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from pydantic import BaseModel

router = APIRouter()


# ================= DB =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= SCHEMAS =================
class ProjectCreate(BaseModel):
    name: str
    owner_id: int


class AddMember(BaseModel):
    admin_id: int   
    user_id: int
    project_id: int


# ================= CREATE PROJECT =================
@router.post("/create_project")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == project.owner_id).first()

    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create project")

    new_project = models.Project(name=project.name, owner_id=project.owner_id)

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return {"project_id": new_project.id}


# ================= GET PROJECTS =================
@router.get("/projects")
def get_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()


# ================= ADD MEMBER =================
@router.post("/add_member")
def add_member(data: AddMember, db: Session = Depends(get_db)):

    
    admin = db.query(models.User).filter(models.User.id == data.admin_id).first()

    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add members")

    
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    
    project = db.query(models.Project).filter(models.Project.id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    
    existing = db.query(models.ProjectMember).filter(
        models.ProjectMember.user_id == data.user_id,
        models.ProjectMember.project_id == data.project_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Member already added")

    member = models.ProjectMember(
        user_id=data.user_id,
        project_id=data.project_id
    )

    db.add(member)
    db.commit()

    return {"message": "Member added"}