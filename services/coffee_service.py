from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.enums import ChatType
from aiogram.types import User

from sqlalchemy import delete, select, or_, and_
from sqlalchemy.orm import selectinload

from database.db import Session
from database.models import Poll, PollStatus, Vote, VoteType

from utils.dto import PollDTO, VoteDTO
from utils.poll_state import PollState


class CoffeeService:

    @staticmethod
    def is_group(chat_type: str) -> bool:
        return chat_type in (
            ChatType.GROUP,
            ChatType.SUPERGROUP,
        )


    @staticmethod
    def build_meeting(
        time: str,
    ) -> datetime:
        """
        Строит дату встречи по времени HH:MM.

        Если указанное время уже прошло сегодня,
        встреча переносится на завтра.
        """

        now = datetime.now()

        hour, minute = map(
            int,
            time.split(":"),
        )

        meeting = now.replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0,
        )

        if meeting <= now:
            meeting += timedelta(days=1)

        return meeting

    @staticmethod
    def build_meeting_from_time(
        meeting_at: datetime,
        hour: int,
        minute: int,
    ) -> datetime:
        """
        Меняет только время существующей встречи.

        Если получилось прошлое —
        переносит встречу на следующий день.
        """

        meeting = meeting_at.replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0,
        )

        now = datetime.now()

        if meeting <= now:
            meeting += timedelta(days=1)

        return meeting


    @staticmethod
    def hours_left(
        meeting_at: datetime,
    ) -> float:
        return (
            meeting_at - datetime.now()
        ).total_seconds() / 3600


    @staticmethod
    def can_create_normal_poll(
        meeting_at: datetime,
        min_vote_hours: int,
    ) -> bool:
        return (
            CoffeeService.hours_left(meeting_at)
            >= min_vote_hours
        )

    @staticmethod
    def can_create_short_poll(
        meeting_at: datetime,
    ) -> bool:
        return (
            CoffeeService.hours_left(meeting_at)
            > 0
        )


    @staticmethod
    def get_poll_state(
        meeting_at: datetime,
        min_vote_hours: int,
    ) -> PollState:

        hours_left = CoffeeService.hours_left(
            meeting_at,
        )

        return PollState(
            hours_left=hours_left,
            allow_later=hours_left >= min_vote_hours,
        )


    async def get_active_poll(
        self,
        chat_id: int,
    ) -> Poll | None:

        async with Session() as session:

            result = await session.execute(
                select(Poll).where(
                    Poll.chat_id == chat_id,
                    Poll.status == PollStatus.ACTIVE,
                )
            )

            return result.scalar_one_or_none()

    async def create_poll(
        self,
        chat_id: int,
        author_id: int,
        meeting_at: datetime,
        place: str,
        allow_later: bool,
    ) -> Poll:

        async with Session() as session:

            poll = Poll(
                chat_id=chat_id,
                author_id=author_id,
                meeting_at=meeting_at,
                place=place,
                status=PollStatus.ACTIVE,
                allow_later=allow_later,
            )

            session.add(poll)

            await session.commit()
            await session.refresh(poll)

            return poll

    async def set_message_id(
        self,
        poll_id: int,
        message_id: int,
    ):

        async with Session() as session:

            poll = await session.get(
                Poll,
                poll_id,
            )

            if poll is None:
                return

            poll.message_id = message_id

            await session.commit()

    async def save_vote(
        self,
        poll_id: int,
        user,
        vote: VoteType,
    ):

        async with Session() as session:

            await session.execute(
                delete(Vote).where(
                    Vote.poll_id == poll_id,
                    Vote.user_id == user.id,
                )
            )

            session.add(
                Vote(
                    poll_id=poll_id,
                    user_id=user.id,
                    username=user.username,
                    full_name=user.full_name,
                    vote=vote,
                )
            )

            await session.commit()

    async def get_poll(
        self,
        poll_id: int,
    ) -> Poll | None:

        async with Session() as session:

            return await session.get(
                Poll,
                poll_id,
                options=[
                    selectinload(Poll.votes),
                ],
            )

    async def get_poll_dto(
        self,
        poll_id: int,
    ) -> PollDTO | None:

        poll = await self.get_poll(poll_id)

        if poll is None:
            return None

        return PollDTO(
            id=poll.id,
            place=poll.place,
            meeting_at=poll.meeting_at,
            votes=[
                VoteDTO(
                    full_name=v.full_name,
                    vote=v.vote.value,
                )
                for v in poll.votes
            ],
        )

    async def close_poll(
        self,
        poll_id: int,
    ):

        async with Session() as session:

            poll = await session.get(
                Poll,
                poll_id,
            )

            if poll is None:
                return

            poll.status = PollStatus.CLOSED

            await session.commit()

    async def cancel_poll(
        self,
        poll_id: int,
    ):

        async with Session() as session:

            poll = await session.get(
                Poll,
                poll_id,
            )

            if poll is None:
                return

            poll.status = PollStatus.CANCELLED

            await session.commit()

    async def can_manage_poll(
        self,
        poll: Poll,
        user: User,
        bot: Bot,
    ) -> bool:

        if poll.author_id == user.id:
            return True

        member = await bot.get_chat_member(
            poll.chat_id,
            user.id,
        )

        return member.status in (
            "administrator",
            "creator",
        )
    

    async def get_polls_for_worker(self) -> list[Poll]:
        """Получает активные опросы И закрытые опросы, которые еще не откреплены."""
        async with Session() as session:
            result = await session.execute(
                select(Poll).where(
                    or_(
                        Poll.status == PollStatus.ACTIVE,
                        # .is_(False) заменяет == False и полностью устраивает ruff
                        and_(Poll.status == PollStatus.CLOSED, Poll.is_unpinned.is_(False))
                    )
                )
            )
            return list(result.scalars().all())

    # Явно указываем типы int | None и bool | None для соответствия PEP 484
    async def update_reminder_state(
        self, 
        poll_id: int, 
        last_hour: int | None = None, 
        final_sent: bool | None = None
    ):
        """Сохраняет состояние напоминаний в базу данных."""
        async with Session() as session:
            poll = await session.get(Poll, poll_id)
            if poll:
                if last_hour is not None:
                    poll.last_reminder_hour = last_hour
                if final_sent is not None:
                    poll.final_reminder_sent = final_sent
                await session.commit()

    async def mark_as_unpinned(self, poll_id: int):
        """Отмечает в БД, что сообщение опроса было успешно откреплено."""
        async with Session() as session:
            poll = await session.get(Poll, poll_id)
            if poll:
                poll.is_unpinned = True
                await session.commit()

    async def get_later_voters(self, poll_id: int) -> list[Vote]:
        """Получает список голосов пользователей, ответивших 'Отвечу позже'."""
        async with Session() as session:
            result = await session.execute(
                select(Vote).where(
                    Vote.poll_id == poll_id,
                    # ⚠️ ВНИМАНИЕ: Проверьте ваш enum VoteType!
                    # Замените LATER на то название, которое у вас отвечает за "отвечу позже"
                    # (например: VoteType.LATER, VoteType.DELAY, VoteType.THINK и т.д.)
                    Vote.vote == VoteType.LATER,
                )
            )
            return list(result.scalars().all())

coffee_service = CoffeeService()