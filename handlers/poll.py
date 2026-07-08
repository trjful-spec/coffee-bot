from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

from services.coffee_service import coffee_service
from services.permission_service import permission_service
from services.poll_sender import update_poll_message
from services.poll_service import poll_service

router = Router()


@router.message(Command("close"))
async def close_poll(
    message: Message,
    bot: Bot,
):

    poll = await coffee_service.get_active_poll(
        message.chat.id,
    )

    if poll is None:
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
        await message.answer(
            "❌ Только создатель голосования "
            "или администратор группы "
            "может закрыть голосование."
        )
        return

    await poll_service.close_poll(
        poll.id,
    )

    await update_poll_message(
        bot=bot,
        poll_id=poll.id,
    )

    if poll.message_id:

        try:
            await bot.unpin_chat_message(
                chat_id=message.chat.id,
                message_id=poll.message_id,
            )
        except TelegramBadRequest:
            pass

    await message.answer(
        "✅ Голосование закрыто."
    )


@router.message(Command("cancel"))
async def cancel_poll(
    message: Message,
    bot: Bot,
):

    poll = await coffee_service.get_active_poll(
        message.chat.id,
    )

    if poll is None:
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
        await message.answer(
            "❌ Только создатель голосования "
            "или администратор группы "
            "может отменить голосование."
        )
        return

    await poll_service.cancel_poll(
        poll.id,
    )

    await update_poll_message(
        bot=bot,
        poll_id=poll.id,
    )

    if poll.message_id:

        try:
            await bot.unpin_chat_message(
                chat_id=message.chat.id,
                message_id=poll.message_id,
            )
        except TelegramBadRequest:
            pass

    await message.answer(
        "❌ Голосование отменено."
    )


@router.message(Command("time"))
async def change_time(
    message: Message,
    bot: Bot,
):

    args = message.text.split(maxsplit=1)

    if len(args) != 2:
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
        await message.answer(
            "❌ Неверный формат времени."
        )
        return

    poll = await coffee_service.get_active_poll(
        message.chat.id,
    )

    if poll is None:
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
        await message.answer(
            "❌ Только создатель голосования "
            "или администратор группы "
            "может изменить время."
        )
        return

    meeting = poll.meeting_at.replace(
        hour=new_time.hour,
        minute=new_time.minute,
        second=0,
        microsecond=0,
    )

    await poll_service.change_time(
        poll.id,
        meeting,
    )

    await update_poll_message(
        bot=bot,
        poll_id=poll.id,
    )

    await message.answer(
        f"🕘 Время изменено на {meeting:%H:%M}"
    )