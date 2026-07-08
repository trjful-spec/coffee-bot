from datetime import datetime

from aiogram import Bot
from aiogram.enums import ChatType
from aiogram.types import User

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from database.db import Session
from database.models import Poll
from database.models import PollStatus
from database.models import Vote
from database.models import VoteType

from utils.dto import PollDTO
from utils.dto import VoteDTO
from utils.poll_state import PollState


class CoffeeService:

    @staticmethod
    def is_group(chat_type: str) ->bool:
        return chat_type in (
            ChatType.GROUP,
            ChatType.SUPERGROUP,
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
    ) -> Poll:

        async with Session() as session:

            poll = Poll(
                chat_id=chat_id,
                author_id=author_id,
                meeting_at=meeting_at,
                place=place,
                status=PollStatus.ACTIVE,
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

        poll = await self.get_poll(
            poll_id,
        )

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

    @staticmethod
    def get_poll_state(
        meeting_at: datetime,
        min_vote_hours: int,
    ) -> PollState:

        hours_left = (
            meeting_at - datetime.now()
        ).total_seconds() / 3600

        return PollState(
            hours_left=hours_left,
            allow_later=(
                hours_left >= min_vote_hours
            ),
        )


    @staticmethod
    def allow_later_vote(
        meeting_at: datetime,
        min_vote_hours: int,
    ) -> bool:
        return (
            CoffeeService.hours_left(
                meeting_at,
            ) >= min_vote_hours
        )

coffee_service = CoffeeService()