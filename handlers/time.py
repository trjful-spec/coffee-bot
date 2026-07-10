from datetime import datetime

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from services.coffee_service import coffee_service
from services.permission_service import permission_service
from services.poll_service import poll_service
from services.poll_updater import refresh_active_poll

router = Router()


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

    meeting = coffee_service.build_meeting_from_time(
        poll.meeting_at,
        new_time.hour,
        new_time.minute,
    )

    if meeting <= datetime.now():
        await message.answer(
            "❌ Нельзя установить время голосования в прошлом."
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
        f"🕘 Время изменено на {meeting:%d.%m %H:%M}"
    )