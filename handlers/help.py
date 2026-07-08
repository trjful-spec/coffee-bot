from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
async def help_command(message: Message):

    await message.answer(
        "☕ <b>Coffee Bot</b>\n\n"

        "<b>Создать голосование</b>\n"
        "/coffee - будет использовано дефолтное время и место (21:00, Мега)\n"
        "/coffee 15:30 - будет использовано дефолтное место (Мега)\n"
        "/coffee 15:30 Дубровка\n\n"

        "<b>Управление</b>\n"
        "/close — закрыть голосование \n"
        "/cancel — отменить голосование\n"
        "/time HH:MM — изменить время сбора\n"
        "/interval N — изменить минимальный интервал для «Отвечу позже»\n\n"
    )