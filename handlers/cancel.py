from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

from services.coffee_service import coffee_service
from services.settings_service import settings_service
from utils.message_builder import build_poll_text

router = Router()


@router.message(Command("cancel"))
async def cancel_poll(
    message: Message,
):

    settings = await settings_service.get(
        message.chat.id,
    )

    if not coffee_service.is_group(
        message.chat.type,
    ):
        await message.answer(
            "❌ Команда работает только в группах."
        )
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
            "❌ Отменить голосование может только "
            "создатель или администратор."
        )
        return

    await coffee_service.cancel_poll(
        poll.id,
    )

    dto = await coffee_service.get_poll_dto(
        poll.id,
    )

    if poll.message_id:

        try:
            await message.bot.edit_message_text(
                chat_id=poll.chat_id,
                message_id=poll.message_id,
                text="❌ <b>Голосование отменено</b>\n\n"
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
        "❌ Голосование отменено."
    )