from datetime import datetime
from math import floor

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import config

from keyboards.confirm_short_poll import (
    confirm_short_poll_keyboard,
)

from services.coffee_service import coffee_service
from services.poll_sender import send_poll
from services.settings_service import settings_service

from utils.coffee_parser import parse_coffee_command

router = Router()


@router.message(Command("coffee"))
async def coffee(message: Message):

    if not coffee_service.is_group(
        message.chat.type,
    ):
        await message.answer(
            "❌ Команда работает только в группах."
        )
        return

    active = await coffee_service.get_active_poll(
        message.chat.id,
    )

    if active is not None:
        await message.answer(
            "⚠️ Уже есть активное голосование."
        )
        return

    try:
        time, place = parse_coffee_command(
            message.text,
            config.default_time,
            config.default_place,
        )

    except ValueError:

        await message.answer(
            "❌ Неверный формат команды.\n\n"
            "Использование:\n"
            "/coffee\n"
            "/coffee 20:30\n"
            "/coffee 20:30 Парнас"
        )
        return

    meeting = coffee_service.build_meeting(
        time,
    )
    if meeting <= datetime.now():
        await message.answer(
            "❌ Нельзя создать голосование на прошедшее время."
        )
        return

    settings = await settings_service.get(
        message.chat.id,
    )

    state = coffee_service.get_poll_state(
        meeting,
        settings.min_vote_hours,
    )

    #
    # До встречи меньше минимального интервала.
    #
    if not state.allow_later:

        hours_left = max(
            0,
            state.hours_left,
        )

        suggested = max(
            1,
            floor(hours_left),
        )

        await message.answer(
            (
                f"⚠️ До встречи осталось всего "
                f"{hours_left:.1f} ч.\n\n"

                f"Сейчас минимальный интервал "
                f"составляет "
                f"{settings.min_vote_hours} ч.\n\n"

                "Можно:\n"
                "• создать голосование без возможности "
                "«Отвечу позже»;\n"

                "• уменьшить минимальный интервал:\n\n"

                f"/interval {suggested}"
            ),
            reply_markup=confirm_short_poll_keyboard(
                time,
                place,
            ),
        )

        return

    #
    # Создаем обычное голосование.
    #
    poll = await coffee_service.create_poll(
        chat_id=message.chat.id,
        author_id=message.from_user.id,
        meeting_at=meeting,
        place=place,
    )

    await send_poll(
        message,
        poll.id,
    )