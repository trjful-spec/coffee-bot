from datetime import timedelta

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from database.models import PollStatus
from database.models import VoteType

from keyboards.vote import (
    VoteCallback,
    vote_keyboard,
)

from services.coffee_service import coffee_service
from services.settings_service import settings_service

from utils.message_builder import build_poll_text

router = Router()


def later_deadline(
    meeting_at,
    hours: int,
) -> str:
    return (
        meeting_at - timedelta(hours=hours)
    ).strftime("%H:%M")


@router.callback_query(
    VoteCallback.filter(),
)
async def vote(
    callback: CallbackQuery,
    callback_data: VoteCallback,
):

    poll = await coffee_service.get_poll(
        callback_data.poll_id,
    )

    if poll is None:
        await callback.answer(
            "Голосование не найдено.",
            show_alert=True,
        )
        return

    if poll.status != PollStatus.ACTIVE:
        await callback.answer(
            "Голосование уже закрыто.",
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

    if (
        callback_data.vote == "later"
        and not state.allow_later
    ):
        await callback.answer(
            "Время для ответа «Отвечу позже» уже прошло.",
            show_alert=True,
        )
        return

    if callback.from_user is None:
        return

    if callback.bot is None:
        return

    await coffee_service.save_vote(
        poll_id=poll.id,
        user=callback.from_user,
        vote=VoteType(callback_data.vote),
    )

    dto = await coffee_service.get_poll_dto(
        poll.id,
    )

    if dto is None:
        return

    try:
        await callback.message.edit_text(
            build_poll_text(
                dto,
                later_hours=settings.min_vote_hours,
            ),
            reply_markup=vote_keyboard(
                dto,
                show_later=state.allow_later,
                later_until=later_deadline(
                    dto.meeting_at,
                    settings.min_vote_hours,
                ),
            ),
        )

    except TelegramBadRequest:
        pass

    await callback.answer(
        "Ваш голос учтён ✅",
    )