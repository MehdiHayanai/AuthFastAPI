import os
from datetime import datetime, timedelta, timezone

# from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session
from starlette import status

from backend.database import get_db
from backend.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


class UserExistsError(Exception):
    pass


SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if SECRET_KEY is None:
    raise ValueError("SECRET_KEY environment variable is not set.")
if ALGORITHM is None:
    raise ValueError("ALGORITHM environment variable is not set.")

if ACCESS_TOKEN_EXPIRE_MINUTES is None:
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES environment variable is not set.")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
db_dependency = Annotated[Session, Depends(get_db)]


class CreatUserRequest(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=10, pattern="^[a-zA-Z0-9]+$", example="user123"
    )
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with a unique username and password. "
    "The username must be between 3 and 10 characters long, "
    "and can only contain alphanumeric characters. "
    "Example request body: "
    "{ 'username': 'user123', 'password': 'password123' }",
    response_description="The created user's ID, username, and hashed password.",
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "user123",
                        "hash_password": "$2b$12$KIXTO5Fh5Z5Q5Z5Q5Z5Q5u",
                    }
                }
            },
        },
        400: {
            "description": "Bad request, user already exists or validation error",
            "content": {
                "application/json": {"example": {"detail": "User already exists"}}
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            },
        },
    },
)
async def create_user(
    db: db_dependency,
    user: CreatUserRequest,
):
    """
    Create a new user.
    """
    try:
        # check if the user already exists
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            raise UserExistsError("User already exists")
        hashed_password = bcrypt_context.hash(user.password)
        db_user = User(username=user.username, hash_password=hashed_password)
        db.add(db_user)
        db.commit()
        return {
            "id": db_user.id,
            "username": db_user.username,
            "hash_password": db_user.hash_password,
        }
    except UserExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/{username}",
    status_code=status.HTTP_200_OK,
)
async def get_user(
    db: db_dependency,
    username: str,
):
    """
    Get a user by username.
    """
    db_user = db.query(User).filter(User.username == username).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {
        "id": db_user.id,
        "username": db_user.username,
        "hash_password": db_user.hash_password,
    }


async def authenticat_user(
    username: str,
    password: str,
    db: db_dependency,
):
    """
    Authenticate a user.
    """
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        return False
    if not bcrypt_context.verify(password, db_user.hash_password):
        return False
    return db_user


def create_access_token(data: dict):
    """
    Create an access token.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def login_access_token(
    db: db_dependency,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Login and get an access token.
    """
    db_user = await authenticat_user(
        form_data.username,
        form_data.password,
        db,
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": db_user.username, "id": db_user.id},
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    """
    Get the current user from the access token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if user_id is None:
            raise credentials_exception
        if username is None:
            raise credentials_exception

        return {
            "username": username,
            "id": payload.get("id"),
        }
    except JWTError:
        raise credentials_exception
