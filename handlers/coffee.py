from datetime import datetime
import logging
import math

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.coffee_service import coffee_service
from services.poll_sender import send_poll
from services.settings_service import settings_service

from keyboards.confirm_short_poll import (
    confirm_short_poll_keyboard,
)

from utils.coffee_parser import parse_coffee_command

from config import config

logger = logging.getLogger(__name__)

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

    if active:
        await message.answer(
            "⚠️ Голосование уже существует."
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

    meeting = datetime.strptime(
        f"{datetime.now():%Y-%m-%d} {time}",
        "%Y-%m-%d %H:%M",
    )

    settings = await settings_service.get(
        message.chat.id,
    )

    state = coffee_service.get_poll_state(
        meeting,
        settings.min_vote_hours,
    )

    if not state.allow_later:

        suggested = math.floor(state.hours_left)

        if suggested < 0:
            suggested = 0

        await message.answer(
            (
                f"⚠️ До встречи осталось всего {state.hours_left:.1f} ч.\n\n"
                f"Сейчас минимальный интервал составляет "
                f"{settings.min_vote_hours} ч.\n\n"
                "Можно:\n"
                "• оставить текущий интервал и создать голосование;\n"
                "• уменьшить интервал командой\n\n"
                f"/interval {suggested}"
            ),
            reply_markup=confirm_short_poll_keyboard(
                time,
                place,
            ),
        )

    return

    poll = await coffee_service.create_poll(
        chat_id=message.chat.id,
        author_id=message.from_user.id,
        meeting_at=meeting,
        place=place,
    )

    await send_poll(
        message,
        poll.id,
        allow_later=True,
    )