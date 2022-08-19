from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
IP = env.str("IP")  # ip хоста
API_ID = env.str("API_ID") 
API_HASH = env.str("API_HASH")
CHAT_ID = env.str("CHAT_ID")
