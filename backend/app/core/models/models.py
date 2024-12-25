from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import LargeBinary, String, DateTime, Boolean, Integer

from .base import Base


class User(Base):
    email: Mapped[str] = mapped_column(String(256))
    username: Mapped[str] = mapped_column(String(256))
    pass_hash: Mapped[bytes] = mapped_column(LargeBinary())
    time_created: Mapped[datetime] = mapped_column(DateTime())
    time_updated: Mapped[datetime] = mapped_column(DateTime())


class Document(Base):
    name: Mapped[str] = mapped_column(String(256))
    year: Mapped[int | None] = mapped_column(String(256))
    link: Mapped[str] = mapped_column(String(256))
    is_file: Mapped[bool] = mapped_column(Boolean())
    subject_name: Mapped[str] = mapped_column(String(256))
    category_name: Mapped[str] = mapped_column(String(256))
    teacher_name: Mapped[str | None] = mapped_column(String(256))
    semester_num: Mapped[int] = mapped_column(Integer)
    time_created: Mapped[datetime] = mapped_column(DateTime())
    time_updated: Mapped[datetime] = mapped_column(DateTime())
