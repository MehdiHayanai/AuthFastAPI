from datetime import timedelta
from typing import Any, Dict, Optional

from jwt import PyJWTError, decode, encode
from passlib.context import CryptContext

from app.core.config import settings
from app.core.utils import get_current_datetime
from app.schemas.token import TokenPayload
from app.schemas.user import UserInDB

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_token_payload(
    subject: UserInDB, expires_delta: Optional[timedelta] = None
) -> Dict[str, Any]:
    if expires_delta:
        expire = get_current_datetime() + expires_delta
    else:
        expire = get_current_datetime() + timedelta(
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


def create_token_object(
    subject: UserInDB, expires_delta: Optional[timedelta] = None
) -> TokenPayload:
    payload = create_token_payload(subject, expires_delta)
    return TokenPayload(**payload)


def create_jwt_token(data: Dict[str, Any]) -> str:
    encoded_jwt = encode(
        data, settings.SECRET_KEY, algorithm=settings.HASHING_ALGORITHM
    )
    return encoded_jwt


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        decoded_token = decode(
            token, settings.SECRET_KEY, algorithms=[settings.HASHING_ALGORITHM]
        )
        return decoded_token
    except PyJWTError:
        return None
