from app.services.users import Base, create_user, engine, SessionLocal

# 1. Create tables
Base.metadata.create_all(bind=engine)

# 2. Create admin user
db = SessionLocal()
create_user(db, username="", password="", is_admin=False)
db.close()
