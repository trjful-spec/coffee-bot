from aiogram import F
from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message(
    F.pinned_message
    | F.new_chat_members
    | F.left_chat_member
    | F.group_chat_created
    | F.supergroup_chat_created
    | F.channel_chat_created
    | F.message_auto_delete_timer_changed
)
async def service_message(
    _: Message,
):
    """
    Игнорируем сервисные сообщения Telegram.
    Они считаются обработанными и не засоряют лог.
    """
    pass