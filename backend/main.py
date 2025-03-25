from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend.models import User
from backend.routes.auth import router as auth_router

app = FastAPI()
app.include_router(auth_router)

Base.metadata.create_all(bind=engine)


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/", status_code=status.HTTP_200_OK)
async def user(
    db: db_dependency,
    user=None,
):
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
