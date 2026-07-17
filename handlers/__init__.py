from aiogram import Dispatcher

from .start import router as start_router
from .coffee import router as coffee_router
from .votes import router as votes_router
from .interval import router as interval_router
from .confirm_short_poll import router as confirm_short_poll_router
from .close import router as close_router
from .cancel import router as cancel_router
from .help import router as help_router
from .time import router as time_router
# from .debug import router as debug_router
from .service import router as service_router


def register_handlers(
    dp: Dispatcher,
):
    dp.include_router(start_router)
    dp.include_router(coffee_router)
    dp.include_router(votes_router)
    dp.include_router(interval_router)
    dp.include_router(confirm_short_poll_router)
    dp.include_router(close_router)
    dp.include_router(cancel_router)
    dp.include_router(help_router)
    dp.include_router(time_router)
    dp.include_router(service_router)
    
    # dp.include_router(debug_router)