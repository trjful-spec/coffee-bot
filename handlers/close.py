from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from database.models import PollStatus
from services.coffee_service import coffee_service
from utils.message_builder import build_poll_text

router = Router()


@router.message(Command("close"))
async def close_poll(message: Message):

    if not coffee_service.is_group(
        message.chat.type,
    ):
        return

    poll = await coffee_service.get_active_poll(
        message.chat.id,
    )

    if poll is None:
        await message.answer(
            "❌ Нет активного голосования."
        )
        return

    if not await coffee_service.can_manage_poll(
        poll,
        message.from_user,
        message.bot,
    ):
        await message.answer(
            "❌ Закрыть голосование может только "
            "создатель или администратор."
        )
        return

    await coffee_service.close_poll(
        poll.id,
    )

    dto = await coffee_service.get_poll_dto(
        poll.id,
    )

    try:
        await message.bot.edit_message_text(
            chat_id=poll.chat_id,
            message_id=poll.message_id,
            text="🔒 Голосование закрыто\n\n"
            + build_poll_text(dto),
        )
    except TelegramBadRequest:
        pass

    try:
        await message.bot.unpin_chat_message(
            chat_id=poll.chat_id,
            message_id=poll.message_id,
        )
    except TelegramBadRequest:
        pass

    await message.answer(
        "✅ Голосование закрыто."
    )