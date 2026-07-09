from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, Boolean, Column
from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy import String

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class PollStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class VoteType(str, Enum):
    YES = "yes"
    NO = "no"
    LATER = "later"


class Poll(Base):

    __tablename__ = "polls"

    id: Mapped[int] = mapped_column(primary_key=True)

    chat_id: Mapped[int] = mapped_column(BigInteger)

    message_id: Mapped[int | None]

    author_id: Mapped[int] = mapped_column(BigInteger)

    place: Mapped[str]

    allow_later = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    meeting_at: Mapped[datetime] = mapped_column(DateTime)

    status: Mapped[PollStatus] = mapped_column(
        SqlEnum(PollStatus),
        default=PollStatus.ACTIVE,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    votes: Mapped[list["Vote"]] = relationship(
        back_populates="poll",
        cascade="all, delete-orphan",
    )


class Vote(Base):

    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True)

    poll_id: Mapped[int] = mapped_column(
        ForeignKey("polls.id")
    )

    user_id: Mapped[int] = mapped_column(BigInteger)

    username: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    full_name: Mapped[str]

    vote: Mapped[VoteType] = mapped_column(
        SqlEnum(VoteType)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    poll: Mapped["Poll"] = relationship(
        back_populates="votes"
    )


class ChatSettings(Base):

    __tablename__ = "chat_settings"

    chat_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    default_place: Mapped[str] = mapped_column(
        default="Мега",
    )

    default_time: Mapped[str] = mapped_column(
        default="21:00",
    )

    min_vote_hours: Mapped[int] = mapped_column(
        default=3,
    )