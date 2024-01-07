# Github.com/Vasusen-code

from .. import bot as Drone
from .. import Bot, AUTH_USERS 
from .. import FORCESUB as fs

from main.plugins.helpers import get_link, join, set_timer, screenshot, check_subscription
from main.plugins.progress import progress_for_pyrogram
from main.Database.database import db
from main.plugins.pyroplug import get_msg

from pyrogram.errors import FloodWait, BadRequest
from pyrogram import Client, filters, idle
from ethon.pyfunc import video_metadata
from telethon import events

import re, time, asyncio
# from decouple import config

message = "Send me the message link you want to start saving from, as a reply to this message."
     
errorC = """Error: Couldn't start client by Login credentials, Please logout and login again."""

@Drone.on(events.NewMessage(incoming=True, pattern='/free'))
async def free(event):
    if not (await db.get_process(event.sender_id))["process"]:
        return
    if (await db.get_process(event.sender_id))["batch"]:
        return await event.reply("Use /cancel to stop batch.")
    await event.reply("Done, try after 10 minutes.")
    await asyncio.sleep(600)
    return await db.rem_process(int(event.sender_id))
   
@Drone.on(events.NewMessage(incoming=True, from_users=AUTH_USERS, pattern="^/afree (.*)"))
async def afree(event):
    id = event.pattern_match.group(1)
    await db.rem_process(int(id))

@Drone.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def clone(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply.text == message:
            return
    try:
        link = get_link(event.text)
        if not link:
            return
    except TypeError:
        return
    await check_subscription(event.sender_id)
    s = await db.get_data(event.sender_id)
    if s["dos"] == None:
        await event.reply("⚠️ You are not subscribed to premium bot, contact @ChauhanMahesh_BOT to buy.")
        return
    edit = await event.reply("Processing!")
    if (await db.get_process(event.sender_id))["process"] == True:
        return await edit.edit("❌ Please don't spam links, wait until ongoing process is done.")
    pt = 10
    ut = 10
    if (await db.get_data(event.sender_id))["plan"] == "pro":
        ut = 2
        pt = 2
    to = await db.get_chat(event.chat.id)
    if to == None:
        to = event.sender_id
    if 't.me' in link and not 't.me/c/' in link and not 't.me/b/' in link:
        await db.update_process(event.sender_id)
        try:
            await get_msg(None, Bot, Drone, event.sender_id, to, edit.id, link, 0)
        except Exception as e:
            print(e)
            pass
        await set_timer(Drone, event.sender_id, ut) 
        return
    if 't.me/+' in link:
        userbot = ""
        i, h, s = await db.get_credentials(event.chat.id)
        userbot = None
        if i and h and s is not None:
            try:
                userbot = Client("saverestricted", session_string=s, api_hash=h, api_id=int(i))     
                await userbot.start()
            except Exception as e:
                print(e)
                return await edit.edit(str(e))
        else:
            return await edit.edit("⚠️ Your login credentials not found.")
        try: 
            j = await join(userbot, link)
            await edit.edit(j)
        except Exception as e:
            print(e)
            pass
    if 't.me/c/' in link or 't.me/b/' in link:
        userbot = ""
        i, h, s = await db.get_credentials(event.chat.id)
        if i and h and s is not None:
            try:
                userbot = Client("saverestricted", session_string=s, api_hash=h, api_id=int(i))     
                await userbot.start()
            except Exception as e:
                print(e)
                return await edit.edit(str(e))
        else:
            return await edit.edit("⚠️ Your login credentials not found.")
        await db.update_process(event.sender_id)
        try: 
            await get_msg(userbot, Bot, Drone,event.sender_id, to, edit.id, link, 0)
        except Exception as e:
            print(e)
            pass
        await userbot.stop()
        await set_timer(Drone, event.sender_id, ut) 
