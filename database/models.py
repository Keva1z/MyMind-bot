from enum import Enum, auto
from datetime import datetime, timezone, timedelta
from sqlalchemy import BigInteger, String, Boolean, Integer, ForeignKey, DateTime, JSON, Enum as SQLEnum, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, backref
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing import Optional

from typing import Any

def _getrepr(object: Any) -> str:
    """Returns string representation of object's attributes"""
    return ", ".join(f"{k}={v}" for k, v in object.__dict__.items() if not k.startswith('_'))

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Role(Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userid: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    role: Mapped[Role] = mapped_column(SQLEnum(Role), nullable=False, default=Role.USER)

    # Daily
    tasks: Mapped[dict[str, str]] = mapped_column(JSON, nullable=True)
    journal: Mapped[str] = mapped_column(String(10000), nullable=False, default='')

    def __repr__(self):
        return f"User({_getrepr(self)})"
    
class UserSettings(Base):
    __tablename__ = "settings"

    userid: Mapped[int] = mapped_column(BigInteger, nullable=False, primary_key=True)

    # Daily Notes
    notes_link: Mapped[str] = mapped_column(String(100), nullable=True)
    notes_timer: Mapped[dict[str, str]] = mapped_column(JSON, nullable=True)

    # Affirmations
    # * Nothing here until i can imagine smth

    # Timers
    timers: Mapped[dict[str, str]] = mapped_column(JSON, nullable=True)