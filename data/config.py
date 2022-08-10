from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
IP = env.str("ip")
API_ID = env.int("API_ID")
API_HASH = env.str("API_HASH")
CHAT_ID = env.int("CHAT_ID")  # Чат, где будут храниться видео
