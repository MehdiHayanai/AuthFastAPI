from backend.database.database import Base, SessionLocal, engine

__all__ = ["Base", "SessionLocal", "engine"]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
