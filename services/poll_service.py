from datetime import datetime
import logging

from sqlalchemy import select, update

from database.db import Session
from database.models import Poll
from database.models import PollStatus


logger = logging.getLogger(__name__)


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

            logger.info(
                "Poll #%s closed.",
                poll_id,
            )

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

            logger.info(
                "Poll #%s cancelled.",
                poll_id,
            )

    async def change_time(
        self,
        poll_id: int,
        meeting_at: datetime,
    ):

        async with Session() as session:

            result = await session.execute(
                select(Poll.meeting_at)
                .where(Poll.id == poll_id)
            )

            old_meeting_at = result.scalar_one_or_none()

            await session.execute(
                update(Poll)
                .where(Poll.id == poll_id)
                .values(
                    meeting_at=meeting_at,
                )
            )

            await session.commit()

            if old_meeting_at is not None:

                logger.info(
                    (
                        "Poll #%s meeting time changed "
                        "%s -> %s."
                    ),
                    poll_id,
                    old_meeting_at.strftime("%H:%M"),
                    meeting_at.strftime("%H:%M"),
                )

            else:
                logger.info(
                    "Poll #%s meeting time changed to %s.",
                    poll_id,
                    meeting_at.strftime("%H:%M"),
                )


poll_service = PollService()