from dotenv import load_dotenv
import os
from fastapi import Request, HTTPException
from passlib.context import CryptContext
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path


SESSION_VERSION_FILE = "~/.pisco_app_session_version"
load_dotenv(".env")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERNAME = os.environ["APP_USER"]
PASSWORD_HASH = os.environ["APP_PSWD_HASH"]

def login_user(request: Request, username: str, password: str):
    if username != USERNAME:
        return False
    return pwd_context.verify(password, PASSWORD_HASH)

def require_login(request: Request):
    if not request.session.get("username"):
        raise StarletteHTTPException(
            status_code=303,
            headers={"Location": "/login"},
        )

def current_user(request: Request):
    return request.session.get("user")

def load_session_version() -> int:
    path = Path(SESSION_VERSION_FILE).expanduser()
    if not path.exists():
        path.write_text("1")
    return int(path.read_text())

def bump_session_version():
    path = Path(SESSION_VERSION_FILE).expanduser()
    v = load_session_version() + 1
    path.write_text(str(v))

def require_user(request: Request):
    session = request.session
    if not session or session.get("session_version") != load_session_version():
        request.session.clear()
        raise StarletteHTTPException(
            status_code=303,
            headers={"Location": "/login"},
        )
    return session

def require_admin(request: Request):
    user = require_user(request)
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin required")
    return user

def get_current_user(request: Request):
    user = require_user(request)
    if not user:
        request.session.clear()
        raise StarletteHTTPException(
            status_code=303,
            headers={"Location": "/login"},
        )
    return user
