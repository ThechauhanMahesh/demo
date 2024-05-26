#Tg:MaheshChauhan/DroneBots
#Github.com/Vasusen-code

"""
Plugin for both public & private channels!
"""

import asyncio

from .. import bot as Drone, AUTH_USERS
from main.plugins.pyroplug import get_bulk_msg
from main.plugins.helpers import get_link, set_subscription, check_subscription
from main.Database.database import db

from pyrogram import Client, filters, types
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyromod.exceptions import ListenerTimeout

errorC = """Error: Couldn't start client by Login credentials, Please logout and login again."""

batch_link = False

@Drone.on_message(filters=filters.command('cancel') & filters.incoming)
async def cancel(_, message: types.Message):
    if not (await db.get_process(message.from_user.id))["batch"]:
        return await message.reply("No batch active, all previous conversations are cancelled.")
    await db.rem_process(message.from_user.id)
    await message.reply("✅ Done.")

@Drone.on_message(filters=filters.command('myplan') & filters.incoming)
async def myplan(_, message: types.Message):
    data = await db.get_data(message.from_user.id)
    await message.reply(f'**DATE OF SUBSCRIPTION:** {data["dos"]}\n**DATE OF EXPIRY:** {data["doe"]}\n**PLAN:** {data["plan"]}')
    return

@Drone.on_message(filters=filters.command('x') & filters.incoming)
async def ss(_, message: types.Message):
    if AUTH_USERS != message.from_user.id:
        return 
    edit = await message.reply("Processing...")
    msg = message.reply_to_message
    data = str(msg.text).split(" ")
    date = data[1]
    if date == "None":
        date = False
    await set_subscription(int(data[0]), date, int(data[2]), data[3])
    x = await db.get_data(int(data[0]))
    await edit.edit(f'{x}')
    await Drone.send_message(int(data[0]), "Your plan is active now, send /myplan to check.")
    return 

@Drone.on_message(filters=filters.command('caption') & filters.incoming)
async def caption(_, message: types.Message):
    if not (await db.get_data(message.from_user.id))["plan"] == "pro":
        return await message.reply("⚠️ Purchase pro plan.")
    await message.reply(
        "Choose an action", 
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("OFF", "off")],
                [InlineKeyboardButton("ADD", "add")],
                [InlineKeyboardButton("DELETE", "delete")],
                [InlineKeyboardButton("REPLACE", "replace")]
            ]
        )
    )

@Drone.on_callback_query(filters.regex(r"add"))
async def add(_, cb: CallbackQuery):
    await cb.message.delete()
    user_id = cb.from_user.id
    try:
        add = await Drone.ask(chat_id=user_id, text="Send the text you want to add in captions.", filters=filters.text, timeout=60)
    except ListenerTimeout:
        return await Drone.send_message(user_id, "You took too long to respond.")
    await db.add_caption(user_id, add.text)
    await Drone.send_message(user_id, "Done ✅")
        
@Drone.on_callback_query(filters.regex(r"delete"))
async def delete(_, cb: CallbackQuery):
    await cb.message.delete()
    user_id = cb.from_user.id
    try:
        delete = await Drone.ask(chat_id=user_id, text="Send the text you want to delete in captions.", filters=filters.text, timeout=60)
    except ListenerTimeout:
        return await Drone.send_message(user_id, "You took too long to respond.")
    await db.delete_caption(user_id, delete.text)
    await Drone.send_message(user_id, "Done ✅")
        
@Drone.on_callback_query(filters.regex(r"off"))
async def off(_, cb: CallbackQuery):
    await cb.message.delete()
    user_id = cb.from_user.id
    await db.disable_caption(user_id)
    await Drone.send_message(user_id, "No changes will be made in captions ✅")
    
@Drone.on_callback_query(filters.regex(r"replace"))
async def replace(_, cb: CallbackQuery):
    await cb.message.delete()
    user_id = cb.from_user.id
    try:
        delete = await Drone.ask(chat_id=user_id, text="Send the text you want to replace in captions.", filters=filters.text, timeout=60)
        replace = await Drone.ask(chat_id=user_id, text="Send the text you want to replace by in captions.", filters=filters.text, timeout=60)
    except ListenerTimeout:
        return await Drone.send_message(user_id, "You took too long to respond.")
    await db.replace_caption(user_id, {"d":delete.text, "a":replace.text})
    await Drone.send_message(user_id, "Done ✅")

@Drone.on_message(filters=filters.command('batch') & filters.incoming & filters.private)
async def batch(client, message: types.Message):
    global batch_link
    user_id = message.from_user.id
    data = await db.get_data(user_id)
    plan = data["plan"]
    caption_data = await db.get_caption(user_id)
    
    await check_subscription(user_id)

    if plan != "pro":
        await message.reply("⚠️ This bot is only for mega users.")
        return
    
    pr = (await db.get_process(user_id))["process"]
    if pr:
        return await message.reply("⚠️ You've already started one process, wait for it to complete!")
    
    batch_link = True
    try:
        link = await Drone.ask(chat_id=user_id, text="Send me the message link you want to start saving from.", filters=filters.text, timeout=60)
    except ListenerTimeout:
        await message.reply("You took too long to respond.")
    try:
        link = get_link(link.text)
    except Exception:
        return await message.reply("⚠️ No link found.")
    batch_link = True
    try:
        range_ = await Drone.ask(chat_id=user_id, text="Send me the number of files/range you want to save from the given message.", filters=filters.text, timeout=60)
    except ListenerTimeout:
        await message.reply("You took too long to respond.")
        batch_link = False
        return 
    batch_link = False
    try:
        range_ = range_.text
        value = int(range_)
        if value > 1000:
            await message.reply("⚠️ You can only get upto 1000 files in a single batch.")
            return
    except ValueError:
        await message.reply("Range must be an integer!")
        return
            
    i, h, s = await db.get_credentials(user_id)
    chat = await db.get_chat(user_id)
    if chat == None:
        chat = user_id
    userbot = None
    if s:
        userbot = Client("saverestricted", session_string=s, api_hash=h, api_id=int(i))     
    else:
        await message.reply("⚠️ Your login credentials not found.")
        return
    await db.update_process(user_id, batch=True)
    await run_batch(userbot, client, user_id, chat, link, value, caption_data, plan) 
    await db.rem_process(user_id)
            
async def run_batch(userbot, client, sender, chat, link, value, caption_data, plan):
    for i in range(value):
        if i < 50:
            timer = 4
        elif i > 50 and i < 100:
            timer = 6
        elif i > 100:
            timer = 8
        elif i > 500:
            timer = 10
        if not 't.me/c/' in link and not 't.me/b/' in link:
            timer = 10
        try: 
            if not (await db.get_process(sender))["process"]:
                await client.send_message(sender, "✅ Batch completed.")
                break
        except Exception as e:
            print(e)
            await client.send_message(sender, "✅ Batch completed.")
            break
        try: 
            await userbot.start()
        except Exception as e:
            print(e)
            await client.send_message(sender, f'{errorC}\n\n**Error:** {str(e)}')
            break
        try:
            await get_bulk_msg(userbot, client, sender, chat, link, caption_data, i=i, plan=plan) 
        except FloodWait as fw:
            if int(fw.value) > 299:
                await client.send_message(sender, "❌ Cancelling batch since you have floodwait more than 5 minutes.")
                break
            await asyncio.sleep(fw.value + 5)
            await get_bulk_msg(userbot, client, sender, chat, link, i=i)
        await userbot.stop()
        protection = await client.send_message(chat, f"⚠️ Sleeping for `{timer}` seconds to avoid Floodwaits and Protect account!")
        await asyncio.sleep(timer)
        await protection.delete()
