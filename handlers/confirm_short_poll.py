from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.confirm_short_poll import (
    ConfirmShortPollCallback,
)

from services.coffee_service import coffee_service
from services.poll_sender import send_poll

import logging

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(
    ConfirmShortPollCallback.filter(
        ~F.confirm,
    )
)
async def cancel_short_poll(
    callback: CallbackQuery,
):
    logger.info(
        (
            "Short poll creation cancelled "
            "by user=%s in chat=%s."
        ),
        callback.from_user.id,
        callback.message.chat.id,
    )

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
    logger.info(
        (
            "Received short poll confirmation "
            "from user=%s in chat=%s."
        ),
        callback.from_user.id,
        callback.message.chat.id,
    )

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
        logger.warning(
            (
                "User=%s used an expired "
                "short poll button."
            ),
            callback.from_user.id,
        )

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
        logger.warning(
            (
                "Active poll #%s already exists "
                "in chat=%s."
            ),
            active.id,
            callback.message.chat.id,
        )

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
        logger.warning(
            (
                "User=%s attempted to create "
                "short poll for past time (%s)."
            ),
            callback.from_user.id,
            callback_data.time,
        )

        await callback.message.edit_reply_markup()

        await callback.answer(
            "Время встречи уже прошло.",
            show_alert=True,
        )

        return

    if callback.from_user is None:
        logger.warning(
            "Callback has no from_user."
        )
        return

    if callback.bot is None:
        logger.warning(
            "Callback has no bot instance."
        )
        return

    logger.info(
        (
            "Creating short poll "
            "(meeting_at=%s, place='%s')."
        ),
        meeting.strftime(
            "%Y-%m-%d %H:%M",
        ),
        callback_data.place,
    )

    poll = await coffee_service.create_poll(
        chat_id=callback.message.chat.id,
        author_id=callback.from_user.id,
        meeting_at=meeting,
        place=callback_data.place,
        allow_later=True,
    )

    logger.info(
        "Short poll #%s successfully created.",
        poll.id,
    )

    await callback.message.edit_reply_markup()

    await send_poll(
        callback.message,
        poll.id,
    )

    await callback.answer(
        "✅ Голосование создано.",
    )