#Tg:MaheshChauhan/DroneBots
#Github.com/Vasusen-code

"""
Plugin for both public & private channels!
"""

import asyncio
import logging

from .. import CustomBot, bot as Drone, AUTH_USERS
from main.plugins.pyroplug import get_msg
from main.plugins.helpers import extract_tg_link, get_link, rreplace, set_subscription, check_subscription
from main.Database.database import db

from pyrogram import filters, types
from pyrogram.errors import FloodWait, FloodPremiumWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyromod.exceptions import ListenerTimeout

@Drone.on_message(filters=filters.command('cancel') & filters.incoming)
async def cancel(_, message: types.Message):
    if not (await db.get_process(message.from_user.id))["batch"]:
        return await message.reply("No batch active, all previous conversations are cancelled.")
    await db.rem_process(message.from_user.id)
    await message.reply("✅ Done.")

@Drone.on_message(filters=filters.command('myplan') & filters.incoming)
async def myplan(_, message: types.Message):
    await message.reply(f'⚠️ This is a demo bot, buy plan from @DroneBots')
    return

@Drone.on_message(filters=filters.command('caption') & filters.incoming)
async def caption(_, message: types.Message):
    return await message.reply("⚠️ Purchase pro plan from @DroneBots")

@Drone.on_message(filters=filters.command('batch') & filters.incoming & filters.private)
async def batch(client, message: types.Message):
    await message.reply(f'⚠️ This is a demo bot, buy plan with batch from @DroneBots')
