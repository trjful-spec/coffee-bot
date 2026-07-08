from aiogram import Dispatcher

from .start import router as start_router
from .coffee import router as coffee_router
from .votes import router as votes_router
from .interval import router as interval_router
from .confirm_short_poll import router as confirm_short_poll_router


def register_handlers(
    dp: Dispatcher,
):
    dp.include_router(start_router)
    dp.include_router(coffee_router)
    dp.include_router(votes_router)
    dp.include_router(interval_router)
    dp.include_router(confirm_short_poll_router)