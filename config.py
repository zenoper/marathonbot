from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("TOKEN")
ADMIN = env.list("ADMIN")

MAIN_CHANNEL_ID = env.str("MAIN_CHANNEL_ID")
PRIVATE_CHANNEL_LINK = env.str("PRIVATE_CHANNEL_LINK")
REQUIRED_REFERRALS = env.int("REQUIRED_REFERRALS")
DB_USER = env.str("DB_USER")
DB_PASS = env.str("DB_PASS")
DB_NAME = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.int("DB_PORT")