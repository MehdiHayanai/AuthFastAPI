from datetime import datetime, timedelta
from typing import Any

from app.api.dependencies import get_current_active_superuser
from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_jwt_token,
    create_token_payload,
    get_password_hash,
    verify_password,
)
from app.db.models.token import Token
from app.db.models.user import User
from app.schemas.token import Token as TokenSchema
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate, UserInDB
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserSchema)
def register_new_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Create new user.
    """
    # Check if user exists
    user = (
        db.query(User)
        .filter((User.email == user_in.email) | (User.username == user_in.username))
        .first()
    )
    if user:
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists",
        )

    # Create new user
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_superuser=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/register-superuser", response_model=UserSchema)
def register_superuser(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    if not current_user.is_superuser and not current_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action",
        )

    # Check if user exists
    user = (
        db.query(User)
        .filter((User.email == user_in.email) | (User.username == user_in.username))
        .first()
    )
    if user:
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists",
        )

    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_superuser=True,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=TokenSchema)
def login_for_access_token(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Get client info
    ip_address = request.client.host
    user_agent = request.headers.get("User-Agent", "")

    # Create token payload
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    user_in_db = UserInDB(
        email=user.email,
        username=user.username,
        id=user.id,
        hashed_password=user.hashed_password,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
    )
    payload = create_token_payload(user_in_db, access_token_expires)
    access_token = create_jwt_token(payload)
    # Store token in database
    token_expiry = datetime.fromtimestamp(payload["exp"])
    db_token = Token(
        token=access_token,
        expires_at=token_expiry,
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(db_token)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db),
) -> Any:
    """
    Logout user by invalidating their token.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid token format")

    token = auth_header.replace("Bearer ", "")

    # Find and delete token
    db_token = db.query(Token).filter(Token.token == token).first()
    if db_token:
        db.delete(db_token)
        db.commit()
        return {"detail": "Successfully logged out"}

    return {"detail": "Token not found or already invalidated"}
