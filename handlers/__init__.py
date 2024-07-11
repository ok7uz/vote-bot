from aiogram import Dispatcher

from handlers import start, poll


async def setup_handlers(dp: Dispatcher):
    dp.include_routers(start.router, poll.router)
