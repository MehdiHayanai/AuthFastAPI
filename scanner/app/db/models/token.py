from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.config import settings
from app.core.utils import get_current_datetime
from app.db import Base


class Token(Base):
    __tablename__ = settings.TOKEN_TABLE

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=get_current_datetime)
    last_used_at = Column(DateTime, default=get_current_datetime)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    user = relationship("User", back_populates="tokens")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.created_at = get_current_datetime()
        self.last_used_at = self.created_at
