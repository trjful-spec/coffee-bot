from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from database.models import VoteType

from keyboards.vote import (
    VoteCallback,
    vote_keyboard,
)

from services.coffee_service import coffee_service
from services.settings_service import settings_service

from utils.message_builder import build_poll_text

router = Router()


@router.callback_query(
    VoteCallback.filter(),
)
async def vote(
    callback: CallbackQuery,
    callback_data: VoteCallback,
):

    await coffee_service.save_vote(
        poll_id=callback_data.poll_id,
        user=callback.from_user,
        vote=VoteType(callback_data.vote),
    )

    poll = await coffee_service.get_poll_dto(
        callback_data.poll_id,
    )

    if poll is None:
        await callback.answer(
            "Голосование не найдено.",
            show_alert=True,
        )
        return

    settings = await settings_service.get(
        callback.message.chat.id,
    )

    state = coffee_service.get_poll_state(
        poll.meeting_at,
        settings.min_vote_hours,
    )

    try:
        await callback.message.edit_text(
            build_poll_text(
                poll,
                show_later=state.allow_later,
                later_hours=settings.min_vote_hours,
            ),
            reply_markup=vote_keyboard(
                poll,
                show_later=state.allow_later,
            ),
        )

    except TelegramBadRequest:
        pass

    await callback.answer(
        "Ваш голос учтен ✅",
    )