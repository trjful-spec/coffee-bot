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
        ~F.confirm,
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
        F.confirm,
    )
)

async def confirm_short_poll(
    callback: CallbackQuery,
    callback_data: ConfirmShortPollCallback,
):
    #
    # Старые callback содержат HH-MM
    #
    try:
        meeting = coffee_service.build_meeting(
            callback_data.time.replace(
                "-",
                ":",
            )
        )

    except Exception:

        await callback.message.edit_reply_markup()

        await callback.answer(
            "Эта кнопка устарела.",
            show_alert=True,
        )

        return

    #
    # Пока пользователь думал —
    # голосование уже появилось.
    #
    active = await coffee_service.get_active_poll(
        callback.message.chat.id,
    )

    if active is not None:

        await callback.message.edit_reply_markup()

        await callback.answer(
            "⚠️ Уже существует активное голосование.",
            show_alert=True,
        )

        return

    #
    # Если время уже прошло —
    # создавать нельзя.
    #
    if not coffee_service.can_create_short_poll(
        meeting,
    ):

        await callback.message.edit_reply_markup()

        await callback.answer(
            "Время встречи уже прошло.",
            show_alert=True,
        )

        return

    if callback.from_user is None:
        return

    if callback.bot is None:
        return

    #
    # Создаем голосование БЕЗ кнопки
    # "Отвечу позже".
    #
    poll = await coffee_service.create_poll(
        chat_id=callback.message.chat.id,
        author_id=callback.from_user.id,
        meeting_at=meeting,
        place=callback_data.place,
        allow_later=True,
    )

    await callback.message.edit_reply_markup()

    await send_poll(
        callback.message,
        poll.id,
    )

    await callback.answer(
        "✅ Голосование создано.",
    )