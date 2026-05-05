from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from database import engine, Base
import models


from routes import user, project, task


import os
import uvicorn


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(project.router)
app.include_router(task.router)

# IMPORTANT
templates = Jinja2Templates(directory="templates")


@app.get("/")
def home():
    return {"message": "Task Manager Running 🚀"}


@app.get("/dashboard_page", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

@app.get("/login_page", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)