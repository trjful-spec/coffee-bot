from math import floor

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.coffee_service import coffee_service
from services.settings_service import settings_service
from services.poll_updater import refresh_active_poll

import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("interval"))
async def interval(message: Message):

    # Защита для mypy
    if not message.text or not message.bot:
        logger.warning(
            "Message has no text or bot instance."
        )
        return

    logger.info(
        "Received /interval from user=%s in chat=%s.",
        message.from_user.id,
        message.chat.id,
    )

    # if not coffee_service.is_group(
    #     message.chat.type,
    # ):
    #     await message.answer(
    #         "❌ Команда работает только в группах."
    #     )
    #     return

    parts = message.text.split()

    if len(parts) == 1:
        settings = await settings_service.get(
            message.chat.id,
        )

        logger.info(
            (
                "User=%s requested current "
                "interval (%s hours)."
            ),
            message.from_user.id,
            settings.min_vote_hours,
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
        logger.warning(
            (
                "User=%s provided invalid "
                "interval value: '%s'."
            ),
            message.from_user.id,
            parts[1],
        )

        await message.answer(
            "Использование:\n"
            "/interval 2"
        )
        return

    if hours < 0 or hours > 24:
        logger.warning(
            (
                "User=%s attempted to set "
                "invalid interval (%s hours)."
            ),
            message.from_user.id,
            hours,
        )

        await message.answer(
            "Интервал должен быть "
            "от 0 до 24 часов."
        )
        return

    # Проверяем наличие активного голосования
    poll = await coffee_service.get_active_poll(
        message.chat.id,
    )

    if poll:
        hours_left = coffee_service.hours_left(
            poll.meeting_at,
        )

        # Если новый интервал больше,
        # чем осталось времени до встречи.
        if hours > hours_left:

            old_hours = hours

            if hours_left < 1:
                hours = 0
            else:
                hours = floor(
                    hours_left,
                )

            logger.info(
                (
                    "Interval automatically "
                    "changed %s -> %s for "
                    "poll #%s (hours_left=%.1f)."
                ),
                old_hours,
                hours,
                poll.id,
                hours_left,
            )

            await message.answer(
                (
                    "⚠️ Выбранный интервал "
                    "больше, чем время до встречи.\n"
                    "Для текущего голосования "
                    "автоматически установлено: "
                    f"<b>{hours} ч.</b>"
                ),
                parse_mode="HTML",
            )

    logger.info(
        (
            "Setting interval=%s hours "
            "for chat=%s."
        ),
        hours,
        message.chat.id,
    )

    await settings_service.set_interval(
        message.chat.id,
        hours,
    )

    await refresh_active_poll(
        message.bot,
        message.chat.id,
    )

    await message.answer(
        f"✅ Интервал напоминаний теперь {hours} ч."
    )

    logger.info(
        (
            "Interval successfully changed "
            "to %s hours for chat=%s."
        ),
        hours,
        message.chat.id,
    )