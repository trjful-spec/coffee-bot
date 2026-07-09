from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "☕ Coffee Bot запущен.\n\n"
        "Используйте /coffee для создания голосования."
    )
