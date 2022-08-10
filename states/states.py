from aiogram.dispatcher.filters.state import StatesGroup, State


class GroupOfStates(StatesGroup):
    settings = State()
    audio_quality_settings = State()
    video_quality_settings = State()
    choosing_fragments_to_mark = State()
    choosing_fragments_to_delete = State()
