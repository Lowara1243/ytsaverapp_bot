from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="❓ FAQ"),
            KeyboardButton(text='⚙️ Settings')
        ]
    ],
    resize_keyboard=True
)


settings = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Return')
        ],
        [
            KeyboardButton(text='Audio quality'),
            KeyboardButton(text='Video quality'),
        ],
        [
            KeyboardButton(text='Fragments to mark'),
            KeyboardButton(text='Fragments to delete')
        ]
    ],
    resize_keyboard=True
)


audio_quality_settings = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Return')
        ],
        [
            KeyboardButton(text='Quality: "best"')
        ],
        [
            KeyboardButton(text='Quality: "medium"'),
            KeyboardButton(text='Quality: "low"')
        ],
        [
            KeyboardButton(text='Quality: "worst"')
        ],
        [
            KeyboardButton(text='no audio')
        ]
    ],
    resize_keyboard=True
)


video_quality_settings = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Return')
        ],
        [
            KeyboardButton(text='Quality: "best"')
        ],
        [
            KeyboardButton(text='Quality: "4320p"'),
            KeyboardButton(text='Quality: "2160p"')
        ],
        [
            KeyboardButton(text='Quality: "1440p"'),
            KeyboardButton(text='Quality: "1080p"')
        ],
        [
            KeyboardButton(text='Quality: "720p"'),
            KeyboardButton(text='Quality: "480p"')
        ],
        [
            KeyboardButton(text='Quality: "360p"'),
            KeyboardButton(text='Quality: "240p"')
        ],
        [
            KeyboardButton(text='Quality: "144p"'),
        ],
        [
            KeyboardButton(text='Quality: "worst"')
        ],
        [
            KeyboardButton(text='no video')
        ]
    ],
    resize_keyboard=True
)

choose_fragments_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Return')
        ],
        [
            KeyboardButton(text='Sponsor')
        ],
        [
            KeyboardButton(text='Intermission / Intro animation')
        ],
        [
            KeyboardButton(text='Self-promotion')
        ],
        [
            KeyboardButton(text='Interaction reminder')
        ],
        [
            KeyboardButton(text='Endcards / Credits')
        ],
        [
            KeyboardButton(text='Preview / Recap')
        ],
        [
            KeyboardButton(text='Music off-topic')
        ]
    ]
)
