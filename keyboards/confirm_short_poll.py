from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ConfirmShortPollCallback(
    CallbackData,
    prefix="shortpoll",
):
    time: str
    place: str
    confirm: bool


def confirm_short_poll_keyboard(
    time: str,
    place: str,
):
    kb = InlineKeyboardBuilder()

    kb.button(
        text="✅ Создать",
        callback_data=ConfirmShortPollCallback(
            time=time.replace(":", "-"),
            place=place,
            confirm=True,
        ),
    )

    kb.button(
        text="❌ Отмена",
        callback_data=ConfirmShortPollCallback(
            time=time.replace(":", "-"),
            place=place,
            confirm=False,
        ),
    )

    kb.adjust(2)

    return kb.as_markup()