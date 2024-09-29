from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    fullname = State()
    date_of_birth = State()
    int_local = State()
    phone_number = State()
    phone_number_int = State()
    grade = State()
    public_private = State()
    SAT = State()
    IELTS = State()
    Duolingo = State()
    visa = State()
    travel_history = State()
    average_funding = State()
    confirmation = State()