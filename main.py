from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from database import engine, Base
import models

from routes import user, project, task

import os
import uvicorn

app = FastAPI()

# 🔥 SAFE DB INIT (no crash)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print("DB ERROR:", e)

# Routers
app.include_router(user.router)
app.include_router(project.router)
app.include_router(task.router)

# 🔥 SAFE TEMPLATE PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.get("/")
def home():
    return {"message": "Task Manager Running 🚀"}


@app.get("/dashboard_page", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="dashboard.html",
    context={}
    )


@app.get("/login_page", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="login.html",
    context={}
    )


# 🔥 RUN CONFIG (Railway compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)