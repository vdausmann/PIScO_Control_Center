from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import declarative_base, Session, sessionmaker, Session
from passlib.context import CryptContext


Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str, is_admin: bool = False):
    user = User(username=username, password_hash=hash_password(password), is_admin=is_admin)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is what you pass to Depends
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db  # yield gives FastAPI a session and ensures cleanup
    finally:
        db.close()
