import os, dotenv

dotenv.load_dotenv(override=True)

class Config:
    bot_token = os.getenv("BOT_TOKEN")
    database_url = os.getenv("DATABASE_URL")
    superadmin_ids = list(map(int, os.getenv("SUPERADMIN_IDS").split(",")))

config = Config()
