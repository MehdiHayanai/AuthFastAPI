import os

from sqlalchemy import Column, Integer, String

from backend.database import Base


class User(Base):
    __tablename__ = os.environ.get("USER_TABLE_NAME")
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hash_password = Column(String)
