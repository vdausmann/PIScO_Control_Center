from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.users import get_user_by_username, get_db
from app.services.security import verify_password
from app.services.auth import load_session_version, bump_session_version, require_admin
from sqlalchemy.orm import Session

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    
    request.session.clear()
    request.session.update({
        "user_id": user.id,
        "username": user.username,
        "is_admin": user.is_admin,
        "session_version": load_session_version(),
    })
    return RedirectResponse(url="/", status_code=303)

@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

@router.post("/admin/logout_all")
def admin_logout_all(admin=Depends(require_admin)):
    bump_session_version()
    return RedirectResponse(url="/login", status_code=303)
