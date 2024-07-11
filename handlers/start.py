from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from handlers.poll import ENTER_TITLE_TEXT, NO_POLLS_TEXT
from keyboards.inline import create_poll_keyboard, yes_or_no_keyboard, delete_poll_list_keyboard
from keyboards.reply import starting_keyboard, DELETE_POLL_TEXT
from models.poll import Poll
from models.user import User
from states.poll import PollCreation
from utils.config import ADMINS

router = Router()
START_TEXT = "<b>Assalomu alaykum</b>.\nSo'rovnoma botga xush kelibsiz!"
ENDED_OR_NOT_TEXT = "<b>❌ Ushbu so'rovnomga ovoz berish to'xtatilgan</b>"
CHOOSE_DELETING_POLL_TEXT = "<b>Yakunlamoqchi bo'lgan so'rovnomani tanlang 👇</b>"
REALLY_WANT_DELETE_TEXT = "<b>❗️ Rostan ham ushbu so'rovnomani yakunlamoqchimisiz?</b>"
DELETED_TEXT = '<b>✅ Yakunlandi</b>'
CANCELED_TEXT = '<b>❌ Bekor qilindi</b>'


@router.message(CommandStart())
async def command_start(message: Message):
    if not await User.exists(id=message.from_user.id):
        await User.create_user(message.from_user)
    text = message.text
    poll_id = text.split()[1] if len(text.split()) > 1 else None
    if poll_id:
        poll = await Poll.get_poll_by_id(poll_id=int(poll_id))
        if poll:
            options = await poll.options.all()
            await message.delete()
            await message.bot.send_chat_action(message.chat.id, 'typing')
            await message.bot.copy_message(chat_id=message.chat.id, from_chat_id=poll.creator_id,
                                           message_id=poll.message_id, reply_markup=create_poll_keyboard(options))
            return
        else:
            await message.answer(ENDED_OR_NOT_TEXT, reply_markup=starting_keyboard(message.from_user.id))
            return

    await message.bot.send_chat_action(message.chat.id, 'typing')
    await message.answer(START_TEXT, reply_markup=starting_keyboard(message.from_user.id))


@router.message(lambda message: message.text == DELETE_POLL_TEXT)
async def command_poll(message: Message, state: FSMContext):
    polls = await Poll.get_all_polls()
    if message.from_user.id in ADMINS:
        if polls:
            await message.bot.send_chat_action(message.chat.id, 'typing')
            await message.answer(CHOOSE_DELETING_POLL_TEXT, reply_markup=delete_poll_list_keyboard(polls))
        else:
            await message.answer(NO_POLLS_TEXT, reply_markup=starting_keyboard(message.from_user.id))


@router.callback_query(lambda query: query.data.startswith("delete-poll:"))
async def delete_poll(query: CallbackQuery, state: FSMContext):
    poll_id = int(query.data.split(":")[1])
    poll = await Poll.get_poll_by_id(poll_id)
    await state.update_data(poll=poll)
    await query.message.delete()
    await query.message.answer(REALLY_WANT_DELETE_TEXT, reply_markup=yes_or_no_keyboard())


@router.callback_query(lambda query: query.data == 'do-delete')
async def do_delete(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    poll = data.get('poll')
    await poll.delete()
    await query.message.delete()
    await query.message.answer(DELETED_TEXT, reply_markup=starting_keyboard(query.from_user.id))
    await state.clear()


@router.callback_query(lambda query: query.data == 'cancel-delete')
async def do_delete(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer(CANCELED_TEXT, reply_markup=starting_keyboard(query.from_user.id))
    await state.clear()
