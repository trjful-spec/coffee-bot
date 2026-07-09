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
        return

    if poll.message_id is None:
        return

    dto = await coffee_service.get_poll_dto(
        poll_id,
    )

    if dto is None:
        return

    settings = await settings_service.get(
        poll.chat_id,
    )

    state = coffee_service.get_poll_state(
        dto.meeting_at,
        settings.min_vote_hours,
    )

    try:

        logger.debug(
            "Meeting: %s",
            dto.meeting_at,
        )

        logger.debug(
            "Interval: %s",
            settings.min_vote_hours,
        )

        logger.debug(
            "Allow later: %s",
            state.allow_later,
        )

        logger.debug(
            "Text:\n%s",
            build_poll_text(
                dto,
                later_hours=settings.min_vote_hours,
            ),
        )

        logger.debug(
            "Later until: %s",
            later_deadline(
                dto.meeting_at,
                settings.min_vote_hours,
            ),
        )

        await bot.edit_message_text(
            chat_id=poll.chat_id,
            message_id=poll.message_id,
            text=build_poll_text(
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

    except TelegramBadRequest as e:

        if "message is not modified" in str(e):
            return

        raise