from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_superuser, get_current_user
from app.api.routes.v1 import USER_ROUTER_PREFIX
from app.core.database import get_db
from app.db.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.user import UserUpdate

router = APIRouter(prefix=USER_ROUTER_PREFIX, tags=["users"])


@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update current user.
    """
    # Update user fields
    for field, value in user_in.model_dump(exclude_unset=True).items():
        if field == "is_superuser" and value and not current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to update this field",
            )
        
        if field == "is_active" and not value and not current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to deactivate this account",
            )

        setattr(current_user, field, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


# Admin-only endpoint example
@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Retrieve users. Only for superusers.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users
