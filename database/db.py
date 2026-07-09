from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from .models import Base

DATABASE_URL = "sqlite+aiosqlite:///coffee.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

Session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

async def init_db():

    async with engine.begin() as conn:

        # Создаем таблицы, если их еще нет
        await conn.run_sync(
            Base.metadata.create_all,
        )

        # Обновляем старую БД (если колонка уже существует —
        # SQLite выбросит исключение, которое мы игнорируем)
        try:
            await conn.execute(
                text(
                    """
                    ALTER TABLE chat_settings
                    ADD COLUMN min_vote_hours INTEGER DEFAULT 3
                    """
                )
            )
        except Exception:
            pass

        try:
            await conn.execute(
                text("""
                    ALTER TABLE polls
                    ADD COLUMN allow_later BOOLEAN DEFAULT 1
                """)
            )

        except Exception:
            pass