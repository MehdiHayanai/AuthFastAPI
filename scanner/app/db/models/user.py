from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.config import settings
from app.db import Base


class User(Base):
    __tablename__ = settings.USER_TABLE

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")
