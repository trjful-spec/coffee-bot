from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.coffee_service import coffee_service
from services.settings_service import settings_service
from services.poll_updater import refresh_active_poll

router = Router()


@router.message(Command("interval"))
async def interval(message: Message):

    if not coffee_service.is_group(
        message.chat.type,
    ):
        return

    parts = message.text.split()

    if len(parts) == 1:

        settings = await settings_service.get(
            message.chat.id,
        )

        await message.answer(
            "☕ Настройки голосования\n\n"
            f"Минимальный интервал:\n"
            f"{settings.min_vote_hours} ч."
        )

        return

    try:
        hours = int(parts[1])
    except ValueError:

        await message.answer(
            "Использование:\n"
            "/interval 2"
        )

        return

    if hours < 0 or hours > 24:

        await message.answer(
            "Интервал должен быть от 0 до 24 часов."
        )

        return

    await settings_service.set_interval(
        message.chat.id,
        hours,
    )

    await refresh_active_poll(
        message.bot,
        message.chat.id,
    )

    await message.answer(
        f"✅ Минимальный интервал изменён на {hours} ч."
    )

    poll = await coffee_service.get_active_poll(
        message.chat.id,
    )

    if poll:
        from services.poll_sender import (
            update_poll_message,
        )

        await update_poll_message(
            bot=message.bot,
            poll_id=poll.id,
        )

    poll = await coffee_service.get_active_poll(
        message.chat.id,
    )

    if poll is not None:
        from services.poll_sender import update_poll_message

        await update_poll_message(
            bot=message.bot,
            poll_id=poll.id,
        )

    await message.answer(
        f"✅ Минимальный интервал изменён на {hours} ч."
    )