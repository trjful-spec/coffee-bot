from sqlalchemy import select

from database.db import Session
from database.models import ChatSettings


class SettingsService:

    async def get(self, chat_id: int) -> ChatSettings:

        async with Session() as session:

            settings = await session.get(
                ChatSettings,
                chat_id,
            )

            if settings is None:

                settings = ChatSettings(
                    chat_id=chat_id,
                )

                session.add(settings)

                await session.commit()

                await session.refresh(settings)

            return settings

    async def set_interval(
        self,
        chat_id: int,
        hours: int,
    ):

        async with Session() as session:

            settings = await session.get(
                ChatSettings,
                chat_id,
            )

            if settings is None:

                settings = ChatSettings(
                    chat_id=chat_id,
                )

                session.add(settings)

            settings.min_vote_hours = hours

            await session.commit()


settings_service = SettingsService()