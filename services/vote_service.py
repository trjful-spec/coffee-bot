import logging

from sqlalchemy import delete, select

from database.db import Session
from database.models import Vote, VoteType


logger = logging.getLogger(__name__)


class VoteService:

    async def save_vote(
        self,
        poll_id: int,
        user,
        vote: VoteType,
    ):

        async with Session() as session:

            result = await session.execute(
                select(Vote.vote).where(
                    Vote.poll_id == poll_id,
                    Vote.user_id == user.id,
                )
            )

            old_vote = result.scalar_one_or_none()

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

            if old_vote is None:
                logger.info(
                    "Poll #%s: user %s voted %s.",
                    poll_id,
                    user.id,
                    vote.value,
                )
            else:
                logger.info(
                    "Poll #%s: user %s changed vote %s -> %s.",
                    poll_id,
                    user.id,
                    old_vote,
                    vote.value,
                )


vote_service = VoteService()