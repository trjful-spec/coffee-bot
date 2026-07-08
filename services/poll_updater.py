from aiogram import Bot

from services.coffee_service import coffee_service
from services.poll_sender import update_poll_message


async def refresh_active_poll(
    bot: Bot,
    chat_id: int,
):
    """
    Обновляет сообщение активного голосования,
    если оно существует.
    """

    poll = await coffee_service.get_active_poll(
        chat_id,
    )

    if poll is None:
        return

    await update_poll_message(
        bot=bot,
        poll_id=poll.id,
    )