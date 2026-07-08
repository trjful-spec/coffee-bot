from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class VoteCallback(
    CallbackData,
    prefix="vote",
):
    poll_id: int
    vote: str


def vote_keyboard(
    poll,
    show_later: bool = True,
) -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder()

    kb.button(
        text="✅ Иду",
        callback_data=VoteCallback(
            poll_id=poll.id,
            vote="yes",
        ),
    )

    kb.button(
        text="❌ Не иду",
        callback_data=VoteCallback(
            poll_id=poll.id,
            vote="no",
        ),
    )

    if show_later:
        kb.button(
            text="🤔 Отвечу позже",
            callback_data=VoteCallback(
                poll_id=poll.id,
                vote="later",
            ),
        )

    if show_later:
        kb.adjust(3)
    else:
        kb.adjust(2)

    return kb.as_markup()