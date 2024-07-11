from aiogram import Bot
from aiogram.types import BotCommandScopeDefault
from loguru import logger
from tortoise import Tortoise

from utils.config import COMMANDS
from utils.database import init_db

async def on_startup() -> None:
    logger.debug("Bot is starting...")
    await init_db()


async def on_shutdown():
    logger.debug("Bot is shutting down...")
    await Tortoise.close_connections()


async def is_user_subscribed(bot, user_id, channel_id):
    member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
    return member.status in ['member', 'administrator', 'creator']


async def set_commands(telegram_bot: Bot):
    try:
        await telegram_bot.set_my_commands(COMMANDS, scope=BotCommandScopeDefault())
        logger.info("Commands set successfully")
    except Exception as e:
        logger.error(f"Error setting commands: {e}")
