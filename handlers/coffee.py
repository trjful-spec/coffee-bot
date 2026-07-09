from math import floor

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import config
from services.coffee_service import coffee_service
from services.poll_sender import send_poll
from services.settings_service import settings_service
from utils.coffee_parser import parse_coffee_command

router = Router()


@router.message(Command("coffee"))
async def coffee(message: Message):

    if not coffee_service.is_group(
        message.chat.type,
    ):
        await message.answer(
            "❌ Команда работает только в группах."
        )
        return

    active = await coffee_service.get_active_poll(
        message.chat.id,
    )

    if active is not None:
        await message.answer(
            "⚠️ Уже есть активное голосование."
        )
        return

    try:
        time, place = parse_coffee_command(
            message.text,
            config.default_time,
            config.default_place,
        )

    except ValueError:

        await message.answer(
            "❌ Неверный формат команды.\n\n"
            "Использование:\n"
            "/coffee\n"
            "/coffee 20:30\n"
            "/coffee 20:30 Парнас"
        )
        return

    settings = await settings_service.get(
        message.chat.id,
    )

    meeting = coffee_service.build_meeting(
        time,
    )

    if not coffee_service.can_create_short_poll(
        meeting,
    ):
        await message.answer(
            "❌ Нельзя создать голосование на прошедшее время."
        )
        return

    hours_left = coffee_service.hours_left(
        meeting,
    )

    # Если текущий интервал больше, чем осталось времени до встречи
    if settings.min_vote_hours > hours_left:
        # Если до встречи меньше часа, ставим интервал 0, 
        # чтобы дедлайн кнопки "Отвечу позже" не уходил в прошлое
        if hours_left < 1:
            suggested = 0
        else:
            suggested = floor(hours_left)
        
        # Автоматически обновляем интервал в базе данных
        await settings_service.set_interval(
            message.chat.id,
            suggested
        )
        
        await message.answer(
            # f"🔄 Текущий интервал ({settings.min_vote_hours} ч.) был слишком большим.\n"
            f"Автоматически установлен интервал: <b>{suggested} ч.</b>",
            parse_mode="HTML"
        )

    #
    # Создаем голосование. Кнопка "Отвечу позже" теперь будет выводиться всегда.
    # Благодаря интервалу 0 (при времени < 1ч) кнопка не исчезнет из клавиатуры.
    #
    poll = await coffee_service.create_poll(
        chat_id=message.chat.id,
        author_id=message.from_user.id,
        meeting_at=meeting,
        place=place,
        allow_later=True,
    )

    await send_poll(
        message,
        poll.id,
    )