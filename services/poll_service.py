from datetime import datetime

from sqlalchemy import update

from database.db import Session
from database.models import Poll
from database.models import PollStatus


class PollService:

    async def close_poll(
        self,
        poll_id: int,
    ):

        async with Session() as session:

            await session.execute(
                update(Poll)
                .where(Poll.id == poll_id)
                .values(
                    status=PollStatus.CLOSED,
                )
            )

            await session.commit()

    async def cancel_poll(
        self,
        poll_id: int,
    ):

        async with Session() as session:

            await session.execute(
                update(Poll)
                .where(Poll.id == poll_id)
                .values(
                    status=PollStatus.CANCELLED,
                )
            )

            await session.commit()

    async def change_time(
        self,
        poll_id: int,
        meeting_at: datetime,
    ):

        async with Session() as session:

            await session.execute(
                update(Poll)
                .where(Poll.id == poll_id)
                .values(
                    meeting_at=meeting_at,
                )
            )

            await session.commit()


poll_service = PollService()