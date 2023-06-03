# Github.com/Vasusen-code

from .. import bot as Drone
from .. import Bot, AUTH_USERS 

from main.plugins.helpers import get_link, join, set_timer, screenshot
from main.plugins.progress import progress_for_pyrogram
from main.Database.database import db
from main.plugins.pyroplug import get_msg

from pyrogram.errors import FloodWait, BadRequest
from pyrogram import Client, filters, idle
from ethon.pyfunc import video_metadata
from telethon import events, Button

import re, time, asyncio
from decouple import config

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
    trial = await db.get_trial(event.sender_id)
    if trial == 5:
          return await event.reply("Your free trial is now over, buy premium subscription from @DroneBOTS to continue.")
    x = await force_sub(event.sender_id)
    if x == True:
        return await event.reply("To use this bot you must join these channels." buttons=[[Button.url("DRONE BOTS", url="t.me/dronebots"), Button.url("SRCB", url="t.me/save_restrict_content")]])
    edit = await event.reply("Processing!")
    if (await db.get_process(event.sender_id))["process"] == True:
        return await edit.edit("Please don't spam links, wait until ongoing process is done.")
    to = event.sender_id
    if 't.me' in link and not 't.me/c/' in link and not 't.me/b/' in link:
        await db.update_process(event.sender_id)
        try:
            await get_msg(None, Bot, Drone, event.sender_id, to, edit.id, link, 0)
        except Exception as e:
            print(e)
            pass
        await set_timer(Drone, event.sender_id, 120) 
        return
    if 't.me/+' in link:
        return await event.reply("Join channels by yourself manually.")
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
            return await edit.edit("Your login credentials not found.")
        await db.update_process(event.sender_id)
        try: 
            await get_msg(userbot, Bot, Drone,event.sender_id, to, edit.id, link, 0)
        except Exception as e:
            print(e)
            pass
        await userbot.stop()
        await set_timer(Drone, event.sender_id, 300) 
        await db.update_trial(event.sender_id)
        await event.send_message(event.sender_id, f"You have {(await db.get_trial(event.sender_id)) - 1} trials left.")
        
