from typing import List

from aiogram.types import BotCommand
from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    db_url: str

    class Config:
        env_file = ".env"


ADMINS = [884898025]
START_COMMAND_DESCRIPTION = 'Start | Restart'

predefined_channels = [
    {'name': 'Osiyo Xalqaro Universiteti', 'id': -1001531148425},
    {'name': 'OXU Students', 'id': -1001958249407},
    {'name': 'OXU Life', 'id': -1002047515668}
]

COMMANDS: List[BotCommand] = [
    BotCommand(command="/start", description=START_COMMAND_DESCRIPTION)
]
