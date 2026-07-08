from datetime import datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.confirm_short_poll import (
    ConfirmShortPollCallback,
)
from services.coffee_service import coffee_service
from services.poll_sender import send_poll

router = Router()


@router.callback_query(
    ConfirmShortPollCallback.filter(
        F.confirm == False,
    )
)
async def cancel_short_poll(
    callback: CallbackQuery,
):
    await callback.message.edit_reply_markup()

    await callback.answer(
        "Создание голосования отменено.",
    )


@router.callback_query(
    ConfirmShortPollCallback.filter(
        F.confirm == True,
    )
)
async def confirm_short_poll(
    callback: CallbackQuery,
    callback_data: ConfirmShortPollCallback,
):
    meeting = datetime.strptime(
        f"{datetime.now():%Y-%m-%d} {callback_data.time}",
        "%Y-%m-%d %H:%M",
    )

    poll = await coffee_service.create_poll(
        chat_id=callback.message.chat.id,
        author_id=callback.from_user.id,
        meeting_at=meeting,
        place=callback_data.place,
    )

    await callback.message.edit_reply_markup()

    await send_poll(
        callback.message,
        poll.id,
        allow_later=False,
    )

    await callback.answer(
        "Голосование создано.",
    )