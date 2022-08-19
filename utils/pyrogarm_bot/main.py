from pyrogram import Client
from data import config
import cv2

API_ID = config.API_ID
API_HASH = config.API_HASH
CHAT_ID = config.CHAT_ID

app = Client("account", api_id=API_ID, api_hash=API_HASH)


async def get_history():
    global messages
    async with app:
        async for message in app.get_chat_history(chat_id=CHAT_ID):
            if message.video is not None:
                return message.video.file_id
            if message.audio is not None:
                return message.audio.file_id
            if message.animation is not None:
                return message.animation.file_id
            if message.document is not None:
                return message.document.file_id


async def send_video(filename, thumbnail_filename, text):
    vid = cv2.VideoCapture(filename)
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width, height = int(width), int(height)
    cap = cv2.VideoCapture(filename)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = round(frame_count / fps)
    async with app:
        await app.send_video(chat_id=CHAT_ID, video=filename, caption=f'{filename}',
                             thumb=thumbnail_filename, width=width, height=height, duration=duration)


async def send_audio(filename, thumbnail_filename):
    async with app:
        await app.send_audio(chat_id=CHAT_ID, audio=filename, caption=filename, thumb=thumbnail_filename)


async def test():
    async with app:
        async for message in app.get_chat_history(chat_id=CHAT_ID):
            print(message)


if __name__ == '__main__':
    app.run(test())
