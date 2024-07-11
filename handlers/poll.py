from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.exceptions import TelegramBadRequest

from keyboards.inline import create_poll_list_keyboard, create_poll_keyboard, create_channel_keyboard, \
    create_channel_poll_keyboard, channel_subscribe_keyboard, create_sending_channel_keyboard
from keyboards.reply import VOTE_BUTTON_TEXT, CREATE_POLL_TEXT, complete_options_keyboard, COMPLETE_OPTIONS_TEXT, \
    starting_keyboard
from models.channel import PollChannel
from models.poll import Poll, PollOption
from models.poll_message import PollMessage
from models.vote import Vote
from states.poll import PollCreation
from utils.config import ADMINS
from utils.misc import is_user_subscribed

router = Router()

ENTER_TITLE_TEXT = "So'rovnoma sarlavhasini kiriting"
ENTER_POST_TEXT = "So'rovnoma matnini kiriting"
ENTER_OPTIONS_TEXT = "Ovoz berish uchun so'rovnomani variantlarini yozing (vergul orqali ajrating)"
CHOOSE_POLL_TEXT = "Quyida ko'rsatilgan so'rovnomalardan birini tanlang 👇"
SELECT_CHANNEL_TEXT = "So'rovnoma uchun a'zo bo'lish kerak bo'lgan kanllarni tanlang 👇"
SELECT_SENDING_CHANNEL_TEXT = "So'rovnomani yuboradigan kanallarni tanlang 👇"
ALREADY_VOTED_TEXT = "❗Sizning ovozingiz qabul qilinmadi. Siz ushbu so'rovnomaga ovoz bergansiz."
VOTED_TEXT = '✅ Sizning "<b>{}</b>" ga bergan ovozingiz muvaffaqiyatli qabul qilindi!'
ONLY_VIEW_TEXT = "Bu shunchaki ko'rish uchun"
SUBSCRIBE_FOR_VOTE_TEXT = "So'rovnomaga ovoz berish uchun quyidagi kanallarga azo bo'ling 👇"
SEND_OPTIONS_TEXT = "⚠️ Ovoz berish uchun so'rovnoma variantlari ketma-ket yuboring"
SENT_TO_CHANNELS_TEXT = '✅ So\'rovnoma kanallarga yuborildi'
OPTIONS_ADDED_TEXT = '✅ So\'rovnoma variantlari qo\'shildi'
ADDED_TEXT = '➕ Qo\'shildi'
NO_POLLS_TEXT = '<b>❌ So\'rovnomalar mavjud emas</b>'


@router.message(lambda message: message.text == CREATE_POLL_TEXT)
async def command_poll(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.bot.send_chat_action(message.chat.id, 'typing')
        await message.answer(ENTER_TITLE_TEXT)
        await state.set_state(PollCreation.title)


@router.message(PollCreation.title)
async def set_poll_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.bot.send_chat_action(message.chat.id, 'typing')
    await message.answer(ENTER_POST_TEXT)
    await state.set_state(PollCreation.post)


@router.message(PollCreation.post)
async def set_poll_post(message: Message, state: FSMContext):
    await state.update_data(post_message_id=message.message_id)
    await message.bot.send_chat_action(message.chat.id, 'typing')
    await message.answer(SEND_OPTIONS_TEXT, reply_markup=complete_options_keyboard())
    await state.set_state(PollCreation.options)


@router.message(PollCreation.options and (lambda message: message.text not in [COMPLETE_OPTIONS_TEXT, VOTE_BUTTON_TEXT]))
async def set_poll_options(message: Message, state: FSMContext):
    if await state.get_state():
        option = message.text
        data = await state.get_data()
        options = data.get('options', [])
        options.append(option)
        await state.update_data(options=options)
        await message.bot.send_chat_action(message.chat.id, 'typing')
        await message.answer(ADDED_TEXT)
        await state.set_state(PollCreation.options)
    else:
        await state.clear()


@router.message(PollCreation.options and (lambda message: message.text == COMPLETE_OPTIONS_TEXT))
async def complete_poll_options(message: Message, state: FSMContext):
    await message.bot.send_chat_action(message.chat.id, 'typing')
    await message.answer(OPTIONS_ADDED_TEXT, reply_markup=ReplyKeyboardRemove())
    await message.answer(SELECT_CHANNEL_TEXT, reply_markup=create_channel_keyboard())
    await state.set_state(PollCreation.channels)


@router.callback_query(lambda c: c.data and c.data.startswith('channel:'))
async def process_channel_selection(query: CallbackQuery, state: FSMContext):
    channel_id = int(query.data.split(':')[1])
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    if channel_id not in selected_channels:
        selected_channels.append(channel_id)
        await query.message.edit_reply_markup(reply_markup=create_channel_keyboard(selected_channels))
        await state.update_data(selected_channels=selected_channels)
    else:
        selected_channels.remove(channel_id)
        await query.message.edit_reply_markup(reply_markup=create_channel_keyboard(selected_channels))
        await state.update_data(selected_channels=selected_channels)


@router.callback_query(lambda c: c.data == 'channel-complete')
async def complete_channel_selection(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    poll = await Poll.create_poll(title=data['title'], creator_id=query.from_user.id,
                                  message_id=data['post_message_id'])
    selected_channels = data.get('selected_channels', [])
    for option in data['options']:
        await PollOption.create_poll_option(option.strip(), poll)
    for channel_id in selected_channels:
        channel = await query.bot.get_chat(channel_id)
        await PollChannel.create_poll_channel(poll_id=poll.id, channel_id=int(channel.id), name=channel.title,
                                              link=channel.invite_link)
    await query.bot.send_chat_action(query.message.chat.id, 'typing')
    bot_info = await query.bot.get_me()
    bot_link = f"https://t.me/{bot_info.username}"
    options = await poll.options.all()
    await state.update_data(poll_id=poll.id)
    await state.update_data(bot_link=bot_link)
    await state.update_data(options=options)
    await query.bot.copy_message(
        chat_id=query.message.chat.id,
        from_chat_id=query.message.chat.id,
        message_id=data['post_message_id'],
        reply_markup=create_channel_poll_keyboard(options, poll.id, bot_link)
    )
    try:
        await query.message.delete()
    except TelegramBadRequest:
        pass
    await query.message.answer(SELECT_SENDING_CHANNEL_TEXT, reply_markup=create_sending_channel_keyboard())
    await state.set_state(PollCreation.send)


@router.callback_query(lambda c: c.data and c.data.startswith('sending:'))
async def process_channel_selection(query: CallbackQuery, state: FSMContext):
    channel_id = int(query.data.split(':')[1])
    data = await state.get_data()
    selected_channels = data.get('sending_channels', [])
    if channel_id not in selected_channels:
        selected_channels.append(channel_id)
        await query.message.edit_reply_markup(reply_markup=create_sending_channel_keyboard(selected_channels))
        await state.update_data(sending_channels=selected_channels)
    else:
        selected_channels.remove(channel_id)
        await query.message.edit_reply_markup(reply_markup=create_sending_channel_keyboard(selected_channels))
        await state.update_data(sending_channels=selected_channels)


@router.callback_query(lambda c: c.data == 'sending-complete')
async def complete_channel_selection(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sending_chanels = data.get('sending_channels', [])
    for channel_id in sending_chanels:
        message = await query.bot.copy_message(
            chat_id=channel_id,
            from_chat_id=query.message.chat.id,
            message_id=data['post_message_id'],
            reply_markup=create_channel_poll_keyboard(data['options'], data['poll_id'], data['bot_link'])
        )
        await PollMessage.create(poll_id=data['poll_id'], message_id=message.message_id, chat_id=channel_id)
    try:
        await query.message.delete()
    except TelegramBadRequest:
        pass
    await query.message.answer(SENT_TO_CHANNELS_TEXT, reply_markup=starting_keyboard(query.from_user.id))
    await state.clear()


@router.message(lambda message: message.text == VOTE_BUTTON_TEXT)
async def vote(message: Message):
    polls = await Poll.get_all_polls()
    if polls:
        await message.bot.send_chat_action(message.chat.id, 'typing')
        await message.answer(CHOOSE_POLL_TEXT, reply_markup=create_poll_list_keyboard(polls))
    else:
        await message.answer(NO_POLLS_TEXT, reply_markup=starting_keyboard(message.from_user.id))


@router.callback_query(lambda query: query.data.startswith("poll:"))
async def choose_poll(query: CallbackQuery):
    poll_id = int(query.data.split(":")[1])
    poll = await Poll.get_poll_by_id(poll_id)
    options = await poll.options.all()
    await query.message.delete()
    await query.message.bot.send_chat_action(query.message.chat.id, 'typing')
    await query.bot.copy_message(chat_id=query.message.chat.id, from_chat_id=poll.creator_id,
                                 message_id=poll.message_id, reply_markup=create_poll_keyboard(options))


@router.callback_query(lambda query: query.data.startswith("vote:"))
async def choose_vote(query: CallbackQuery):
    option_id = int(query.data.split(':')[1])
    poll_option = await PollOption.get(id=option_id)
    poll = await poll_option.poll
    voted = await Vote.vote_exists(query.from_user.id, poll.id)
    await query.message.delete()
    await query.message.bot.send_chat_action(query.message.chat.id, 'typing')
    channels = await poll.channels.all()
    subscribed = True
    for channel in channels:
        subscribed = subscribed and await is_user_subscribed(query.bot, query.from_user.id, channel.channel_id)
    if subscribed:
        if voted:
            await query.message.answer(ALREADY_VOTED_TEXT)
            return
        await Vote.create(user_id=query.from_user.id, poll_id=poll.id)
        await poll_option.increase_votes(query.bot)
        await query.message.answer(VOTED_TEXT.format(poll_option.title))
    else:
        await query.message.answer(SUBSCRIBE_FOR_VOTE_TEXT, reply_markup=channel_subscribe_keyboard(channels, query.data))


@router.callback_query(lambda query: query.data.startswith("testvote:"))
async def choose_vote(query: CallbackQuery):
    await query.answer(ONLY_VIEW_TEXT)
