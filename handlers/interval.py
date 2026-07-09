from math import floor

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.coffee_service import coffee_service
from services.settings_service import settings_service
from services.poll_updater import refresh_active_poll

router = Router()


@router.message(Command("interval"))
async def interval(message: Message):
    # Защита для mypy: text и bot гарантированно существуют ниже по коду
    if not message.text or not message.bot:
        return

    if not coffee_service.is_group(
        message.chat.type,
    ):
        return

    parts = message.text.split()

    if len(parts) == 1:
        settings = await settings_service.get(
            message.chat.id,
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
        await message.answer(
            "Использование:\n"
            "/interval 2"
        )
        return

    if hours < 0 or hours > 24:
        await message.answer(
            "Интервал должен быть от 0 до 24 часов."
        )
        return

    # Проверяем, есть ли активное голосование
    poll = await coffee_service.get_active_poll(
        message.chat.id,
    )

    if poll:
        hours_left = coffee_service.hours_left(poll.meeting_at)
        
        # Если новый интервал больше, чем осталось времени до этой встречи
        if hours > hours_left:
            if hours_left < 1:
                hours = 0
            else:
                hours = floor(hours_left)
            
            await message.answer(
                f"⚠️ Выбранный интервал больше, чем время до встречи.\n"
                f"Для текущего голосования автоматически установлено: <b>{hours} ч.</b>",
                parse_mode="HTML"
            )

    await settings_service.set_interval(
        message.chat.id,
        hours,
    )

    await refresh_active_poll(
        message.bot,
        message.chat.id,
    )

    # Отправляем сообщение об успехе ОДИН РАЗ
    await message.answer(
        f"✅ Минимальный интервал изменён на {hours} ч."
    )

    if poll:
        from services.poll_sender import update_poll_message

        await update_poll_message(
            bot=message.bot,
            poll_id=poll.id,
        )