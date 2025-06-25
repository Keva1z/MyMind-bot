from enum import Enum, auto
from datetime import datetime, timezone, timedelta
from sqlalchemy import BigInteger, String, Boolean, Integer, ForeignKey, DateTime, JSON, Enum as SQLEnum, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, backref
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing import Optional
from sqlalchemy.types import TypeDecorator
import json
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime

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

class Task():
    def __init__(self, name: str, description: str, is_completed: bool = False):
        self.name = name
        self.description = description
        self.is_completed = is_completed

    def change_status(self) -> None:
        self.is_completed = not self.is_completed

    def __repr__(self) -> str:
        return f"Task({_getrepr(self)})"
    
class TaskListType(TypeDecorator):
    """Custom type for storing list of Task objects as JSON."""
    impl = JSON

    def process_bind_param(self, value: list["Task"] | None, dialect) -> list[dict] | None:
        if value is None:
            return None
        return [task.__dict__ for task in value]

    def process_result_value(self, value: list[dict] | None, dialect) -> list["Task"] | None:
        if value is None:
            return None
        return [Task(**task_dict) for task_dict in value]

class UserSettings(Base):
    """User settings model."""
    __tablename__ = "settings"

    userid: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("users.userid", ondelete="CASCADE"), 
        nullable=False, 
        primary_key=True
    )

    notes_link: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    time_format: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    timers: Mapped[Optional[dict[str, str]]] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship(
        "User",
        back_populates="settings",
        uselist=False
    )

    @property
    def note_link_parsed(self) -> str:
        if self.notes_link is not None:
            if "{date}" in self.notes_link:
                return self.notes_link.format(date=datetime.strftime(datetime.now(), self.time_format))
        return ""

class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userid: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    role: Mapped[Role] = mapped_column(SQLEnum(Role), nullable=False, default=Role.USER)

    tasks: Mapped[list[Task]] = mapped_column(MutableList.as_mutable(TaskListType), nullable=False, default=list)
    journal: Mapped[str] = mapped_column(String(10000), nullable=False, default="")

    settings: Mapped[Optional[UserSettings]] = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    @property
    def parsed_journal(self) -> str:
        return "\n\n".join(self.list_journal)

    @property
    def list_journal(self) -> list[str]:
        journal = self.journal.split("&&&&&&&&&&")
        return [] if journal[0] in ['', ' '] else journal
    
    def delete_last_note(self) -> str:
        journal = self.list_journal
        if journal != []:
            journal.pop()
            return '&&&&&&&&&&'.join(journal)
        return self.journal

    def __repr__(self) -> str:
        """String representation."""
        return f"User({_getrepr(self)})"