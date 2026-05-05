from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from pydantic import BaseModel
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= SCHEMAS =================
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str


class UserLogin(BaseModel):
    email: str
    password: str


# ================= SIGNUP =================
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):

    hashed_password = pwd_context.hash(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=user.role.lower()   # 🔥 important
    )

    db.add(new_user)
    db.commit()

    return {"message": "User created"}


# ================= LOGIN =================
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Wrong password")

    return {
    "access_token": "ok",
    "user_id": db_user.id,
    "role": db_user.role.lower(),
    "name": db_user.name   # 🔥 ADD THIS
}


# ================= GET USERS =================
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()