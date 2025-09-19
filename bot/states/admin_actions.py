from aiogram.fsm.state import State, StatesGroup


class AdminActions(StatesGroup):
    waiting_for_mailing_text = State()
