from aiogram import Dispatcher

from bot.handlers.start import router as start_router
from bot.handlers.admin.admin_panel import router as admin_panel_router

def setup_handlers(dp: Dispatcher):
    dp.include_routers(
        start_router,
        admin_panel_router
    )
