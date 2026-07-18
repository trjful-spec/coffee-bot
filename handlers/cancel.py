from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

from services.coffee_service import coffee_service
from services.settings_service import settings_service
from utils.message_builder import build_poll_text

import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("cancel"))
async def cancel_poll(
    message: Message,
):
    logger.info(
        "Received /cancel from user=%s in chat=%s.",
        message.from_user.id,
        message.chat.id,
    )

    poll = await coffee_service.get_active_poll(
        message.chat.id,
    )

    if poll is None:
        logger.warning(
            "No active poll found in chat=%s.",
            message.chat.id,
        )

        await message.answer(
            "❌ Нет активного голосования."
        )
        return

    if not await coffee_service.can_manage_poll(
        poll,
        message.from_user,
        message.bot,
    ):
        logger.warning(
            (
                "User=%s attempted to cancel "
                "poll #%s without permissions."
            ),
            message.from_user.id,
            poll.id,
        )

        await message.answer(
            "❌ Отменить голосование может только "
            "создатель или администратор."
        )
        return

    logger.info(
        "Cancelling poll #%s.",
        poll.id,
    )

    await coffee_service.cancel_poll(
        poll.id,
    )

    dto = await coffee_service.get_poll_dto(
        poll.id,
    )

    if dto is None:
        logger.warning(
            "Failed to build DTO for poll #%s.",
            poll.id,
        )

        await message.answer(
            "⚠️ Не удалось получить данные голосования."
        )
        return

    settings = await settings_service.get(
        message.chat.id,
    )

    if poll.message_id:

        try:
            await message.bot.edit_message_text(
                chat_id=poll.chat_id,
                message_id=poll.message_id,
                text=(
                    "❌ <b>Голосование отменено</b>\n\n"
                    + build_poll_text(
                        dto,
                        later_hours=settings.min_vote_hours,
                    )
                ),
                reply_markup=None,
            )

            logger.info(
                "Poll #%s message updated.",
                poll.id,
            )

        except TelegramBadRequest as e:
            logger.exception(
                (
                    "Failed to update message %s "
                    "for poll #%s: %s"
                ),
                poll.message_id,
                poll.id,
                e,
            )

        try:
            await message.bot.unpin_chat_message(
                chat_id=poll.chat_id,
                message_id=poll.message_id,
            )

            logger.info(
                "Poll #%s message unpinned.",
                poll.id,
            )

        except TelegramBadRequest as e:
            logger.exception(
                (
                    "Failed to unpin message %s "
                    "for poll #%s: %s"
                ),
                poll.message_id,
                poll.id,
                e,
            )

    await message.answer(
        "❌ Голосование отменено."
    )

    logger.info(
        "Poll #%s successfully cancelled.",
        poll.id,
    )