from aiogram import Dispatcher

from bot.handlers.start import router as start_router
from bot.handlers.admin.admin_panel import router as admin_panel_router

# def setup_handlers(dp: Dispatcher):
#     dp.include_routers(
#         start_router,
#         admin_panel_router
#     )

import importlib
import importlib.util
from pathlib import Path

def setup_handlers(dp: Dispatcher):
    base_path = Path(__file__).parent
    for handler_type in [""]:
        search_path = base_path / handler_type
        for py_file in search_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            rel_path = py_file.relative_to(Path(__file__).parents[2])
            module_parts = rel_path.with_suffix("").parts
            if "handlers" not in module_parts:
                print(module_parts)

            # Преобразуем в python import path
            module_path = ".".join(rel_path.with_suffix("").parts)
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'router'):
                    print(module_path)
                    dp.include_router(module.router)
            except Exception as e:
                print(module_parts)
                print(f"Ошибка при импорте {module_path}: {e}")
