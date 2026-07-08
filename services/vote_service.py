from sqlalchemy import delete

from database.db import Session
from database.models import Vote, VoteType


class VoteService:

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


vote_service = VoteService()