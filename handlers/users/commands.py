import concurrent.futures
import logging
import os
import re

import asyncio
import sqlite3

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from keyboards.default.menu import *
from loader import dp, db, bot
from states.states import GroupOfStates
from utils.pyrogarm_bot.main import get_history, send_video, send_audio
from utils.yt_downloader import download_video

CATEGORIES = (
    'sponsor',
    'intermission / intro animation',
    'endcards / credits',
    'self-promotion',
    'preview / recap',
    'interaction reminder',
    'music off-topic'
)

queue = []
running_rn = False


async def run_blocking_io(func, url, id):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, func, url, id
        )
    return result


@dp.message_handler(Text(equals='Return'), state='*')  # возврат на начальный экран
async def go_back(message: types.Message, state: FSMContext):
    await in_database(message.from_user.id, message.from_user.username)
    await state.finish()
    await message.answer('Wellcome back!', reply_markup=menu)


@dp.message_handler(Text(equals='❓ FAQ'))  # меню настроек (почти готово)
async def show_FAQ(message: types.Message):
    await in_database(message.from_user.id, message.from_user.username)
    await message.answer('This bot helps you to download videos from youtube.com without any problems\n\n'
                         'Here are the answers to some questions:\n\n'
                         'Why is it better than the others?\n'
                         '>The other bots do not cut off the sponsor, and that was a reason for me to create this '
                         'bot\n\n'
                         'Is this bot free?\n'
                         '>Yep, 100% free\n\n'
                         'Why would I download videos via telegram bot?\n'
                         '>There are a few reasons for you to do that:\n'
                         '1) You will not download anything besides your videos file\n'
                         '2) You\'ll gain an ability to watch videos offline whenever and wherever you want\n'
                         '3) Your traffic usage will be reduced because you will not download sponsor segments\n'
                         'And etc')


@dp.message_handler(Text(equals='⚙️ Settings'))  # меню настроек (почти готово)
async def show_settings(message: types.Message):
    await in_database(message.from_user.id, message.from_user.username)
    await GroupOfStates.settings.set()
    await message.answer('Here are the available settings at the moment:',
                         reply_markup=settings)


@dp.message_handler(Text(equals='Audio quality'),
                    state=GroupOfStates.settings)
async def choose_audio_quality(message: types.Message):  # настройка качества звука
    await in_database(message.from_user.id, message.from_user.username)
    await GroupOfStates.audio_quality_settings.set()
    await message.answer(f'Choose the prefered quality of the audio\n'
                         f'Current set to {db.select_user(id=message.from_user.id)[3]}',
                         reply_markup=audio_quality_settings)


@dp.message_handler(Text(equals='Video quality'),
                    state=GroupOfStates.settings)
async def choose_video_quality(message: types.Message):  # настройка качества видео
    await in_database(message.from_user.id, message.from_user.username)
    await GroupOfStates.video_quality_settings.set()
    await message.answer(f'Choose the prefered quality of the video\n'
                         f'Current set to {db.select_user(id=message.from_user.id)[2]}',
                         reply_markup=video_quality_settings)


@dp.message_handler(Text(equals='Fragments to mark'),
                    state=GroupOfStates.settings)
async def choose_fragments_to_mark(message: types.Message):  # выбор фрагментов для последующей их пометки (пункт в меню)
    await in_database(message.from_user.id, message.from_user.username)
    await GroupOfStates.choosing_fragments_to_mark.set()
    await message.answer(f'Choose the fragments of video you want to be marked via sponsorblock\n'
                         f'Current settings: {db.select_user(id=message.from_user.id)[4]}',
                         reply_markup=choose_fragments_keyboard)


@dp.message_handler(Text(equals='Fragments to delete'),
                    state=GroupOfStates.settings)
async def choose_fragments_to_delete(message: types.Message):  # выбор фрагментов для последующего их удаления (пункт в меню)
    await in_database(message.from_user.id, message.from_user.username)
    await GroupOfStates.choosing_fragments_to_delete.set()
    await message.answer(f'Choose the fragments of video you want to be deleted via sponsorblock\n'
                         f'Current settings: {db.select_user(id=message.from_user.id)[5]}',
                         reply_markup=choose_fragments_keyboard)


@dp.message_handler(state=GroupOfStates.video_quality_settings)
async def set_video_quality(message: types.Message, state: FSMContext):  # выбор качества видео
    await in_database(message.from_user.id, message.from_user.username)
    match message.text.split("Quality: ")[-1]:
        case '"best"' | '"4320p"' | '"2160p"' | '"1440p"' | '"1080p"' | '"720p"' | '"480p"' | '"360p"' | '"240p"' | \
             '"144p"' | '"worst"':
            await message.answer(f'You\'ve chosen: {message.text.split("Quality: ")[-1]}', reply_markup=menu)
            db.change_params(pVidQuality=message.text.split("Quality: ")[-1], id=message.from_user.id)
            await state.finish()
        case 'no video':
            if 'no audio' not in db.select_user(id=message.from_user.id)[3]:
                await message.answer(f'You\'ve chosen: {message.text.split("Quality: ")[-1]}', reply_markup=menu)
                db.change_params(pVidQuality=message.text.split("Quality: ")[-1], id=message.from_user.id)
                await state.finish()
            else:
                await message.answer(f'In order to set "{message.text}", first, choose any audio quality')
        case _:
            await message.answer(f'Please enter valid quality')


@dp.message_handler(state=GroupOfStates.audio_quality_settings)
async def set_audio_quality(message: types.Message, state: FSMContext):  # выбор качества аудио
    await in_database(message.from_user.id, message.from_user.username)
    match message.text.split("Quality: ")[-1]:
        case '"best"' | '"medium"' | '"low"' | '"worst"':
            await message.answer(f'You\'ve chosen: {message.text.split("Quality: ")[-1]}', reply_markup=menu)
            db.change_params(pAudioQuality=message.text.split("Quality: ")[-1], id=message.from_user.id)
            await state.finish()
        case 'no audio':
            if 'no video' not in db.select_user(id=message.from_user.id)[2]:
                await message.answer(f'You\'ve chosen: {message.text.split("Quality: ")[-1]}', reply_markup=menu)
                db.change_params(pAudioQuality=message.text.split("Quality: ")[-1], id=message.from_user.id)
                await state.finish()
            else:
                await message.answer(f'In order to set "{message.text}", first, choose any video quality')
        case _:
            await message.answer(f'Please enter valid quality')


@dp.message_handler(state=GroupOfStates.choosing_fragments_to_mark)
async def set_fragments_to_mark(message: types.Message):  # выбор фрагментов для последующей их пометки (не доделано)
    await in_database(message.from_user.id, message.from_user.username)
    fragments = db.select_user(id=message.from_user.id)[4].split()

    if message.text.lower() not in CATEGORIES:
        await message.answer('Please, choose existing fragment')
        return

    if message.text.lower() not in db.select_user(id=message.from_user.id)[5]:
        if bool(fragments):
            if message.text.lower() not in db.select_user(id=message.from_user.id)[4]:
                fragments = f'{db.select_user(id=message.from_user.id)[4]}, {message.text.lower()}'
                await message.answer(f'You\'ve added: "{message.text.lower()}"\nAnything else?')
            else:
                fragments = db.select_user(id=message.from_user.id)[4].split(', ')
                fragments.remove(message.text.lower())
                fragments = ', '.join(fragments)
                await message.answer(f'You\'ve removed: "{message.text.lower()}"\nAnything else?')
        else:
            fragments = message.text.lower()
            await message.answer(f'You\'ve added: "{message.text.lower()}"\nAnything else?')
        db.change_params(segmentsToMark=fragments, id=message.from_user.id)
    else:
        await message.answer(f'In order to set {message.text}, first remove it from "Fragments to delete"')


@dp.message_handler(state=GroupOfStates.choosing_fragments_to_delete)
async def set_fragments_to_delete(message: types.Message):  # выбор фрагментов для последующего их удаления
    await in_database(message.from_user.id, message.from_user.username)
    fragments = db.select_user(id=message.from_user.id)[5].split()

    if message.text.lower() not in CATEGORIES:
        await message.answer('Please, choose existing fragment')
        return

    if message.text.lower() not in db.select_user(id=message.from_user.id)[4]:
        if bool(fragments):
            if message.text.lower() not in db.select_user(id=message.from_user.id)[5]:
                fragments = f'{db.select_user(id=message.from_user.id)[5]}, {message.text.lower()}'
                await message.answer(f'You\'ve added: "{message.text.lower()}"\nAnything else?')
            else:
                fragments = db.select_user(id=message.from_user.id)[5].split(', ')
                fragments.remove(message.text.lower())
                fragments = ', '.join(fragments)
                await message.answer(f'You\'ve removed: "{message.text.lower()}"\nAnything else?')
        else:
            fragments = message.text.lower()
            await message.answer(f'You\'ve added: "{message.text.lower()}"\nAnything else?')
        db.change_params(segmentsToDelete=fragments, id=message.from_user.id)
    else:
        await message.answer(f'In order to set {message.text}, first remove it from "Fragments to mark"')


@dp.message_handler(state='choosing_new_codec')
async def set_new_codec(message: types.Message):
    await in_database(message.from_user.id, message.from_user.username)
    match message.text.split("Codec: ")[-1]:
        case 'mp3':  # should be used without video
            ...
        case 'mp4':  # should be used with video
            ...
        case 'm4a':  # should be used without video
            ...
        case 'webm':  # should be used with video
            ...


@dp.message_handler(state='*')
async def if_is_link(message: types.Message):
    global queue, running_rn
    await in_database(message.from_user.id, message.from_user.username)
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    is_url = lambda url: url is not None and regex.search(url)
    if is_url(message.text):
        queue.append((message.text, message.from_user.id))
        if running_rn:
            await message.answer(f'Your link was added to a queue\n'
                                 f'Current length of queue: {len(queue)}')
            return
        await message.answer('Bot has recieved url...')
        while len(queue) != 0:
            running_rn = True
            user_link = queue[0][0]
            user_id = queue[0][1]

            try:
                result = await run_blocking_io(download_video, user_link, user_id)
                filename, thumbnail_filename, ext = result
            except Exception as e:
                logging.exception(e)
                await bot.send_message(text='It seems that the link was invalid', chat_id=user_id)
                queue.pop(0)
                return
            await bot.send_message(text='Bot downloaded video, sending to user...', chat_id=user_id)

            match ext:
                case 'mp4':
                    await send_video(filename, thumbnail_filename)
                case _:
                    await send_audio(filename, thumbnail_filename)

            file_id = await get_history()

            match ext:
                case 'mp4':
                    await bot.send_video(video=file_id, caption=filename.rsplit('.', 1)[0], chat_id=user_id)
                case _:
                    try:
                        await bot.send_audio(audio=file_id, caption=filename.rsplit('.', 1)[0], chat_id=user_id)
                    except:
                        await bot.send_document(document=file_id, caption=filename.rsplit('.', 1)[0], chat_id=user_id)

            os.remove(filename)
            os.remove(thumbnail_filename)
            queue.pop(0)
        running_rn = False
    else:
        await message.answer('I don\'t know such a command')


async def in_database(userID, name):
    if userID not in db.select_all_users():
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
            pass
