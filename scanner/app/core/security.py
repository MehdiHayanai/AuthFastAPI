from datetime import timedelta
from typing import Any, Dict, Optional

import jwt
from app.core.config import settings
from app.core.utils import get_current_datetime
from app.schemas.user import UserInDB
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_token_payload(
    subject: UserInDB, expires_delta: Optional[timedelta] = None
) -> Dict[str, Any]:
    if expires_delta:
        expire = get_current_datetime + expires_delta
    else:
        expire = get_current_datetime + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {
        "exp": expire,
        "sub": subject.email,
        "ip_address": subject.ip_address,
        "username": subject.username,
        "user_id": subject.id,
    }
    return to_encode


def create_jwt_token(data: Dict[str, Any]) -> str:
    encoded_jwt = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return decoded_token
    except jwt.PyJWTError:
        return None
