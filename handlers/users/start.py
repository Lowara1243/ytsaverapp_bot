import sqlite3

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from keyboards.default.menu import menu
from loader import dp, db


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    userID = message.from_user.id
    name = message.from_user.username
    settings = ({'video_quality': '1080p',
                 'audio_quality': 'best',
                 'segments_to_mark': '',
                 'segments_to_delete': 'sponsor'})  # default settings

    try:
        db.add_user(name=name, id=userID,  # 1, 0
                    pVidQuality=settings['video_quality'],  # 2
                    pAudioQuality=settings['audio_quality'],  # 3
                    segmentsToMark=settings['segments_to_mark'],  # 4
                    segmentsToDelete=settings['segments_to_delete'])  # 5
    except sqlite3.IntegrityError:
        print('Already exists')

    await message.answer(f"Hello, {message.from_user.username}!", reply_markup=menu)
