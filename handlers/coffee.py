from math import floor

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import config
from services.coffee_service import coffee_service
from services.poll_sender import send_poll
from services.settings_service import settings_service
from utils.coffee_parser import parse_coffee_command

import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("coffee"))
async def coffee(message: Message):

    logger.info(
        "Received /coffee from user=%s in chat=%s.",
        message.from_user.id,
        message.chat.id,
    )

    active = await coffee_service.get_active_poll(
        message.chat.id,
    )

    if active is not None:
        logger.warning(
            "Active poll #%s already exists in chat=%s.",
            active.id,
            message.chat.id,
        )

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
        logger.warning(
            (
                "Invalid /coffee command from "
                "user=%s: %s"
            ),
            message.from_user.id,
            message.text,
        )

        await message.answer(
            "❌ Неверный формат команды.\n\n"
            "Использование:\n"
            "/coffee\n"
            "/coffee 20:30\n"
            "/coffee 20:30 Парнас"
        )
        return

    settings = await settings_service.get(
        message.chat.id,
    )

    meeting = coffee_service.build_meeting(
        time,
    )

    if not coffee_service.can_create_short_poll(
        meeting,
    ):
        logger.warning(
            (
                "User=%s attempted to create "
                "poll for past time (%s)."
            ),
            message.from_user.id,
            time,
        )

        await message.answer(
            "❌ Нельзя создать голосование "
            "на прошедшее время."
        )
        return

    hours_left = coffee_service.hours_left(
        meeting,
    )

    current_interval = settings.min_vote_hours

    # Если интервал больше оставшегося времени,
    # автоматически уменьшаем его.
    if current_interval >= hours_left:

        if hours_left < 1:
            suggested = 0
        else:
            suggested = floor(
                hours_left / 2,
            )

        logger.info(
            (
                "Interval for chat=%s changed "
                "%s -> %s (hours_left=%.1f)."
            ),
            message.chat.id,
            current_interval,
            suggested,
            hours_left,
        )

        await settings_service.set_interval(
            message.chat.id,
            suggested,
        )

        await message.answer(
            (
                f"🔄 Текущий интервал "
                f"({current_interval} ч.) был "
                f"слишком большим, так как "
                f"до встречи осталось всего "
                f"{hours_left:.1f} ч.\n"
                f"⚙️ Автоматически установлен "
                f"интервал: <b>{suggested} ч.</b>"
            ),
            parse_mode="HTML",
        )

        current_interval = suggested

    logger.info(
        (
            "Creating poll "
            "(meeting_at=%s, place='%s')."
        ),
        meeting.strftime(
            "%Y-%m-%d %H:%M",
        ),
        place,
    )

    poll = await coffee_service.create_poll(
        chat_id=message.chat.id,
        author_id=message.from_user.id,
        meeting_at=meeting,
        place=place,
        allow_later=True,
    )

    logger.info(
        "Poll #%s successfully created.",
        poll.id,
    )

    await send_poll(
        message,
        poll.id,
    )