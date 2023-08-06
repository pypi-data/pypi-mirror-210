from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
)
from datetime import datetime

from ...database import Base


class UserWatchlistModel(Base):
    __tablename__ = 'user_watchlists'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), nullable=False)
    resource_type = Column(String(128), nullable=False, index=True)
    resource_id = Column(String(50), nullable=False, index=True)
    is_active = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
