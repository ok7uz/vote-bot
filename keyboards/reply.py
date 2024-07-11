from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from utils.config import ADMINS

VOTE_BUTTON_TEXT = '☑️ OVOZ BERISH'
CREATE_POLL_TEXT = '➕ SO\'ROVNOMA YARATISH'
DELETE_POLL_TEXT = '🚫 SO\'ROVNOMANI YAKUNLASH'
COMPLETE_OPTIONS_TEXT = 'KEYINGISI ▶️'


def starting_keyboard(user_id: int):
    keyboard = [[KeyboardButton(text=VOTE_BUTTON_TEXT)]]
    if user_id in ADMINS:
        keyboard.append([KeyboardButton(text=CREATE_POLL_TEXT)])
        keyboard.append([KeyboardButton(text=DELETE_POLL_TEXT)])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def complete_options_keyboard():
    keyboard = [[KeyboardButton(text=COMPLETE_OPTIONS_TEXT)]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
