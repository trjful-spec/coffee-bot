from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

from services.coffee_service import coffee_service
from services.settings_service import settings_service
from utils.message_builder import build_poll_text

router = Router()


@router.message(Command("close"))
async def close_poll(
    message: Message,
):

    # if not coffee_service.is_group(
    #     message.chat.type,
    # ):
    #     await message.answer(
    #         "❌ Команда работает только в группах."
    #     )
    #     return

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

    settings = await settings_service.get(
        message.chat.id,
    )

    await coffee_service.close_poll(
        poll.id,
    )

    dto = await coffee_service.get_poll_dto(
        poll.id,
    )

    if dto is None:
        await message.answer(
            "⚠️ Голосование уже закрыто."
        )
        return

    try:
        await message.bot.edit_message_text(
            chat_id=poll.chat_id,
            message_id=poll.message_id,
            text="🔒 <b>Голосование закрыто</b>\n\n"
            + build_poll_text(
                dto,
                later_hours=settings.min_vote_hours,
            ),
            reply_markup=None,
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