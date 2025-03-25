import os

from app.core.utils import get_current_datetime
from app.db import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Token(Base):
    __tablename__ = os.environ.get("TOKENS_TABLE_NAME")

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=get_current_datetime)
    last_used_at = Column(DateTime, default=get_current_datetime)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    user = relationship("User", back_populates="tokens")
