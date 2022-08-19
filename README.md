# ytsaverapp_bot
It's a telegram bot that helps user to download video without sponsor segments

### Features
- Cuts off/Marks down the segments via SponsorBlock API
- Allows to download audio without video and video without audio
- Allows to choose video/audio quality

### Installation
1. Clone the project
`git clone https://github.com/Lowara1243/ytsaverapp_bot`

2. Go to the project directory
`cd my-project`


3. Install dependencies:
- Use pip to install all the required libraries
`pip -r requirements.txt`

- Install FFmpeg
`https://ffmpeg.org/download.html`

4. After that, open .env file with your text editor and set your own parameters
`nano .env`

Of these, the mandatory:
- BOT_TOKEN
- API_HASH
- API_ID
- CHAT_ID

CHAT_ID is required only to avoid the telegram's file size limit.
Also, don't forget to make the bot an administrator in the chat where it will post videos.

5. Run app.py via python
`python app.py`

When the bot will try to send a file for the first time, it will ask you to log in to your telegram account in the console.
