from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from keyboards.vote import vote_keyboard

from services.coffee_service import coffee_service
from services.settings_service import settings_service

from utils.message_builder import (
    build_poll_text,
    later_deadline,
)

import logging

logger = logging.getLogger(__name__)


async def send_poll(
    source_message: Message,
    poll_id: int,
):

    dto = await coffee_service.get_poll_dto(
        poll_id,
    )

    if dto is None:
        logger.error(
            "Failed to build DTO for poll #%s.",
            poll_id,
        )

        await source_message.answer(
            "Ошибка создания голосования."
        )

        return

    settings = await settings_service.get(
        source_message.chat.id,
    )

    state = coffee_service.get_poll_state(
        dto.meeting_at,
        settings.min_vote_hours,
    )


    msg = await source_message.answer(
        build_poll_text(
            dto,
            later_hours=settings.min_vote_hours,
        ),
        reply_markup=vote_keyboard(
            dto,
            show_later=state.allow_later,
            later_until=later_deadline(
                dto.meeting_at,
                settings.min_vote_hours,
            ),
        ),
    )

    await coffee_service.set_message_id(
        dto.id,
        msg.message_id,
    )

    try:
        await msg.pin(
            disable_notification=True,
        )

    except TelegramBadRequest:

        logger.error(
            (
                "Failed to pin message %s "
                "for poll #%s."
            ),
            msg.message_id,
            poll_id,
        )

        await source_message.answer(
            "⚠️ Не удалось закрепить сообщение.\n"
            "Выдайте боту право закреплять сообщения."
        )


async def update_poll_message(
    bot: Bot,
    poll_id: int,
):

    poll = await coffee_service.get_poll(
        poll_id,
    )

    if poll is None:
        logger.warning(
            "Poll #%s was not found.",
            poll_id,
        )

        return

    if poll.message_id is None:
        logger.warning(
            "Poll #%s has no message_id.",
            poll_id,
        )

        return

    dto = await coffee_service.get_poll_dto(
        poll_id,
    )

    if dto is None:
        logger.warning(
            "Failed to build DTO for poll #%s.",
            poll_id,
        )

        return

    settings = await settings_service.get(
        poll.chat_id,
    )

    state = coffee_service.get_poll_state(
        dto.meeting_at,
        settings.min_vote_hours,
    )

    reply_markup = None

    if poll.status.name == "ACTIVE":
        reply_markup = vote_keyboard(
            dto,
            show_later=state.allow_later,
            later_until=later_deadline(
                dto.meeting_at,
                settings.min_vote_hours,
            ),
        )

    try:

        await bot.edit_message_text(
            chat_id=poll.chat_id,
            message_id=poll.message_id,
            text=build_poll_text(
                dto,
                later_hours=settings.min_vote_hours,
            ),
            reply_markup=reply_markup,
        )

    except TelegramBadRequest as e:

        if "message is not modified" in str(e):
            return

        logger.exception(
            (
                "Telegram rejected update of "
                "message %s for poll #%s: %s"
            ),
            poll.message_id,
            poll_id,
            e,
        )

        raise