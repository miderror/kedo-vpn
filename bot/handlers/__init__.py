from aiogram import Dispatcher

from .common_actions import router as common_actions_router
from .connect import router as connect_router
from .menu import router as menu_router
from .referral import router as referral_router
from .start import router as start_router
from .subscription import router as subscription_router


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_routers(
        start_router,
        menu_router,
        subscription_router,
        referral_router,
        connect_router,
        common_actions_router,
    )
