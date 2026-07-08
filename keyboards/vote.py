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
    later_until: str | None = None,
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

        text = "🤔 Отвечу позже"

        if later_until:
            text = f"🤔 Отвечу до {later_until}"

        kb.button(
            text=text,
            callback_data=VoteCallback(
                poll_id=poll.id,
                vote="later",
            ),
        )

        kb.adjust(3)

    else:
        kb.adjust(2)

    return kb.as_markup()