from datetime import timedelta

from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.confirm_short_poll import (
    ConfirmShortPollCallback,
)

from services.coffee_service import coffee_service
from services.poll_sender import send_poll
from services.settings_service import settings_service

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
    # кто-то уже создал голосование.
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

    settings = await settings_service.get(
        callback.message.chat.id,
    )

    now = coffee_service.hours_left(
        meeting,
    )

    #
    # Уже прошло.
    #
    if now <= 0:

        await callback.message.edit_reply_markup()

        await callback.answer(
            "Время встречи уже прошло.",
            show_alert=True,
        )

        return

    #
    # Проверяем,
    # что интервал не изменился.
    #
    if now >= settings.min_vote_hours:

        await callback.message.edit_reply_markup()

        await callback.answer(
            "Теперь голосование можно создать сразу.\n"
            "Используйте /coffee ещё раз.",
            show_alert=True,
        )

        return

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
    )

    await callback.answer(
        "✅ Голосование создано.",
    )