from BABYMUSIC import app
from pyrogram.errors import RPCError, UserAlreadyParticipant, ChatAdminRequired, InviteRequestSent, UserNotParticipant
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton, Message, ChatJoinRequest
from pyrogram import Client, filters, enums
from pyrogram.enums import ParseMode, ChatMemberStatus
from logging import getLogger
from BABYMUSIC.utils.database import add_served_chat, get_assistant, is_active_chat
from BABYMUSIC.misc import SUDOERS
import asyncio
import random
import os

LOGGER = getLogger(__name__)

class WelDatabase:
    def __init__(self):
        self.data = {}

    async def find_one(self, chat_id):
        return chat_id in self.data

    async def add_wlcm(self, chat_id):
        if chat_id not in self.data:
            self.data[chat_id] = {"state": "on"}  # Default state is "on"

    async def rm_wlcm(self, chat_id):
        if chat_id in self.data:
            del self.data[chat_id]

wlcm = WelDatabase()

class temp:
    ME = None
    CURRENT = 2
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None

@app.on_message(filters.command("welcome") & ~filters.private)
async def auto_state(_, message):
    usage = "**ᴜsᴀɢᴇ:**\n**⦿ /welcome [on|off]**"
    if len(message.command) == 1:
        return await message.reply_text(usage)
    
    chat_id = message.chat.id
    user = await app.get_chat_member(message.chat.id, message.from_user.id)
    
    if user.status in (
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER,
    ):
        A = await wlcm.find_one(chat_id)
        state = message.text.split(None, 1)[1].strip().lower()
        
        if state == "off":
            if A:
                await message.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ !**")
            else:
                await wlcm.add_wlcm(chat_id)
                await message.reply_text(f"**ᴅɪsᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ** {message.chat.title}")
        
        elif state == "on":
            if not A:
                await wlcm.add_wlcm(chat_id)  # Corrected from rm_wlcm to add_wlcm for "on"
                await message.reply_text(f"**ᴇɴᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ** {message.chat.title}")
        else:
            await message.reply_text(usage)
    else:
        await message.reply("**sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇɴᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ!**")

@app.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(_, member: ChatMemberUpdated):
    chat_id = member.chat.id
    count = await app.get_chat_members_count(chat_id)
    A = await wlcm.find_one(chat_id)

    # If the welcome message is disabled for the chat, do nothing
    if A:
        return

    user = None
    if member.new_chat_member:
        user = member.new_chat_member.user
    elif member.old_chat_member:
        user = member.old_chat_member.user
    
    if not user:
        return  # Exit if no user found in the update
    
    try:
        # Welcome message
        welcome_message = f"👋 {user.first_name}, Wᴇʟᴄᴏᴍᴇ Tᴏ {member.chat.title}!\n\n" \
                          "• I Hᴏᴘᴇ Yᴏᴜ Aʀᴇ Fɪɴᴇ!\n\n" \
                          "• Pʟᴇᴀsᴇ Aʟᴡᴀʏs Fᴏʟʟᴏᴡ Tʜᴇ Gʀᴏᴜᴘ Rᴜʟᴇs!\n" \
                          "────────────────────\n" \
                          f"ᴛ ᴏ ᴛ ᴀ ʟ ᴍ ᴇ ᴍ ʙ ᴇ ʀ: {count}\n" \
                          "────────────────────"
        
        # Creating an inline button to "Join 👋" with the link
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Join 👋", url="https://t.me/HINDII_CHATTING")]]
        )

        # Send the welcome message with the inline button
        await app.send_message(chat_id, welcome_message, reply_markup=keyboard)
    except Exception as e:
        LOGGER.error(f"Error sending welcome message: {e}")
