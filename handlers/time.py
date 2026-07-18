from datetime import datetime

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from services.coffee_service import coffee_service
from services.permission_service import permission_service
from services.poll_service import poll_service
from services.poll_updater import refresh_active_poll

import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("time"))
async def change_time(
    message: Message,
    bot: Bot,
):
    logger.info(
        "Received /time from user=%s in chat=%s.",
        message.from_user.id,
        message.chat.id,
    )

    args = message.text.split(
        maxsplit=1,
    )

    if len(args) != 2:
        logger.warning(
            (
                "User=%s provided invalid "
                "/time command format."
            ),
            message.from_user.id,
        )

        await message.answer(
            "Использование:\n"
            "/time 20:30"
        )
        return

    try:
        new_time = datetime.strptime(
            args[1],
            "%H:%M",
        ).time()

    except ValueError:
        logger.warning(
            (
                "User=%s provided invalid "
                "time value: '%s'."
            ),
            message.from_user.id,
            args[1],
        )

        await message.answer(
            "❌ Неверный формат времени."
        )
        return

    poll = await coffee_service.get_active_poll(
        message.chat.id,
    )

    if poll is None:
        logger.warning(
            "No active poll found in chat=%s.",
            message.chat.id,
        )

        await message.answer(
            "⚠️ Активного голосования нет."
        )
        return

    allowed = await permission_service.can_manage(
        bot=bot,
        poll=poll,
        chat_id=message.chat.id,
        user_id=message.from_user.id,
    )

    if not allowed:
        logger.warning(
            (
                "User=%s attempted to change "
                "time for poll #%s without "
                "permissions."
            ),
            message.from_user.id,
            poll.id,
        )

        await message.answer(
            "❌ Только создатель голосования "
            "или администратор группы "
            "может изменить время."
        )
        return

    meeting = coffee_service.build_meeting_from_time(
        poll.meeting_at,
        new_time.hour,
        new_time.minute,
    )

    if meeting <= datetime.now():
        logger.warning(
            (
                "User=%s attempted to set "
                "past meeting time (%s) "
                "for poll #%s."
            ),
            message.from_user.id,
            args[1],
            poll.id,
        )

        await message.answer(
            "❌ Нельзя установить время "
            "голосования в прошлом."
        )
        return

    await poll_service.change_time(
        poll.id,
        meeting,
    )

    await refresh_active_poll(
        bot,
        message.chat.id,
    )

    await message.answer(
        f"🕘 Время изменено на "
        f"{meeting:%d.%m %H:%M}"
    )