from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.config import predefined_channels

COPLETE_CHANNEL_SELECT_TEXT = 'KEYINGISI ▶️'
SUBSCRIBED_TEXT = "✅ A'ZO BO'LDIM"


def create_channel_keyboard(selected_channels=None):
    if selected_channels is None:
        selected_channels = []
    keyboard = []
    for channel in predefined_channels:
        if channel['id'] in selected_channels:
            keyboard.append([InlineKeyboardButton(text=f"✅  {channel['name']}", callback_data=f'channel:{channel['id']}')])
        else:
            keyboard.append([InlineKeyboardButton(text=f"🔘  {channel['name']}", callback_data=f'channel:{channel['id']}')])
    keyboard.append([InlineKeyboardButton(text=COPLETE_CHANNEL_SELECT_TEXT, callback_data="channel-complete")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_sending_channel_keyboard(selected_channels=None):
    if selected_channels is None:
        selected_channels = []
    keyboard = []
    for channel in predefined_channels:
        if channel['id'] in selected_channels:
            keyboard.append([InlineKeyboardButton(text=f"✅  {channel['name']}", callback_data=f'sending:{channel['id']}')])
        else:
            keyboard.append([InlineKeyboardButton(text=f"🔘  {channel['name']}", callback_data=f'sending:{channel['id']}')])
    keyboard.append([InlineKeyboardButton(text=COPLETE_CHANNEL_SELECT_TEXT, callback_data="sending-complete")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_poll_keyboard(options: list):
    keyboard = []
    for option in options:
        keyboard.append([InlineKeyboardButton(text=option.title, callback_data=f"vote:{option.id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_channel_poll_keyboard(options: list, poll_id: int, bot_link: str):
    keyboard = []
    for option in options:
        keyboard.append([InlineKeyboardButton(text=f'{option.title} - {option.votes}', url=f"{bot_link}?start={poll_id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_poll_list_keyboard(polls: list):
    keyboard = []
    for i, poll in enumerate(polls):
        keyboard.append([InlineKeyboardButton(text=f'{i + 1}. {poll.title}', callback_data=f"poll:{poll.id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def delete_poll_list_keyboard(polls: list):
    keyboard = []
    for i, poll in enumerate(polls):
        keyboard.append([InlineKeyboardButton(text=f'{i + 1}. {poll.title}', callback_data=f"delete-poll:{poll.id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def channel_subscribe_keyboard(channels, query_data: str):
    keyboard = []
    for channel in channels:
        keyboard.append([InlineKeyboardButton(text=channel.name, url=channel.link)])
    keyboard.append([InlineKeyboardButton(text=SUBSCRIBED_TEXT, callback_data=query_data)])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def yes_or_no_keyboard():
    keyboard = [[InlineKeyboardButton(text="✅", callback_data='do-delete'),
                InlineKeyboardButton(text="❌", callback_data='cancel-delete')]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)