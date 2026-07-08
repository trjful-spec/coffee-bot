from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.coffee_service import coffee_service

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "☕ Coffee Bot запущен.\n\n"
        "Используйте /coffee для создания голосования."
    )
