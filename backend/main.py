from typing import Annotated

from database import Base, SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from backend.models import User

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: User | None, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {
        "id": user.id,
        "username": user.username,
        "hash_password": user.hash_password,
    }
