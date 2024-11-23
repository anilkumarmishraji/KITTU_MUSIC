import asyncio
import importlib
from threading import Thread

from flask import Flask
from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from BABYMUSIC import LOGGER, app, userbot
from BABYMUSIC.core.call import BABY
from BABYMUSIC.misc import sudo
from BABYMUSIC.plugins import ALL_MODULES
from BABYMUSIC.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS

# Flask app
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "BABY Music Bot is running!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8000)

async def init():
    if not config.STRING1:
        LOGGER(__name__).error("String session not filled. Please provide a Pyrogram session.")
        exit()

    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception as e:
        LOGGER(__name__).error(f"Error loading banned users: {e}")
    
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("BABYMUSIC.plugins" + all_module)
    LOGGER("BABYMUSIC.plugins").info("All features loaded successfully!")
    
    await userbot.start()
    await BABY.start()
    try:
        await BABY.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("BABYMUSIC").error(
            "Please start your log group/channel voice chat. Stopping bot..."
        )
        exit()
    except Exception as e:
        LOGGER(__name__).error(f"Error in stream_call: {e}")
    
    await BABY.decorators()
    LOGGER("BABYMUSIC").info("Bot is up and running!")
    await idle()

    # Stop services on exit
    await app.stop()
    await userbot.stop()
    LOGGER("BABYMUSIC").info("Stopping BABY Music Bot.")

def main():
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Start the asyncio event loop for the bot
    asyncio.get_event_loop().run_until_complete(init())

if __name__ == "__main__":
    main()
