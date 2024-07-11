from aiogram.fsm.state import State, StatesGroup


class PollCreation(StatesGroup):
    title = State()
    post = State()
    options = State()
    channels = State()
    send = State()
