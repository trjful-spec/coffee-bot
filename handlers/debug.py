from aiogram import Router
from aiogram.types import Message, CallbackQuery

import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message()
async def unknown_message(
    message: Message,
):
    logger.debug(
        "Unhandled message:\n%s",
        message.model_dump(
            exclude_none=True,
        ),
    )


@router.callback_query()
async def unknown_callback(
    callback: CallbackQuery,
):
    logger.debug(
        "Unhandled callback:\n%s",
        callback.model_dump(
            exclude_none=True,
        ),
    )