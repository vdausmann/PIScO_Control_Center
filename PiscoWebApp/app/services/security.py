from passlib.context import CryptContext
import secrets
from pathlib import Path
import os

def init_secret_key(
    env_var: str = "SECRET_KEY",
    key_file: str = "~/.pisco_app_secret",
    length: int = 64):
    """
    Load SECRET_KEY from environment or persistent file.
    Generates one if missing.
    """
    if env_var in os.environ:
        return os.environ[env_var]

    path = Path(key_file).expanduser()
    if path.exists():
        key = path.read_text().strip()
        os.environ[env_var] = key
        return key

    key = secrets.token_urlsafe(length)
    path.write_text(key)
    path.chmod(0o600)  # owner read/write only
    os.environ[env_var] = key
    # return key


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)
