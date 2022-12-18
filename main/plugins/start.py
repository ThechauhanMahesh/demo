#Github.com/Vasusen-code

import os, asyncio
from .. import bot, ACCESS, MONGODB_URI, API_ID, API_HASH

from telethon import events, Button
from decouple import config
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, FloodWait, PhoneCodeInvalid, PhoneCodeExpired 

from main.plugins.helpers import login, logout
from main.Database.database import Database

st = "Send me __Link__ of any __Public__ channel message to clone it here, For __private__ channel message, First __Login__ then send any __message link__ from your chat.\n\n**SUPPORT:** @TeamDrone\n**DEV:** @MaheshChauhan"

ht = """Help:

**FOR PUBLIC CHANNEL:**
- Send me direct link of message. 

**FOR PRIVATE CHANNEL:**
- Login by API and pyrogram String session
- Then send Link of message of any channel you've joined. 

__>> How to Login?__

- Get API details using @UseTGSbot or you can manually get it from official site my.telegram.org (login and click on api development tools) 

- Get Pyrogram string session from @SessionStringGeneratorZBot 
or https://replit.com/@dashezup/generate-pyrogram-session-string

- send /start and click on Login."""

otp_text = """An OTP has been sent to your number. 

Please send the OTP with space, example: `1 2 3 4 5`."""

@bot.on(events.NewMessage(incoming=True, pattern="/start"))
async def start(event):
    await event.reply(f'{st}', 
                      buttons=[
                              [Button.inline("SET THUMB", data="sett"),
                               Button.inline("REM THUMB", data="remt")],
                              [Button.inline("LOG IN", data="login"),
                               Button.inline("LOG OUT", data="logout")],
                              [Button.inline("HELP", data="help"),
                               Button.url("SOURCE", url="github.com/vasusen-code/saverestrictedcontentbot")],
                              ])
    tag = f'[{event.sender.first_name}](tg://user?id={event.sender_id})'
    await event.client.send_message(int(ACCESS), f'{tag} started the BOT\nUserID: {event.sender_id}') 
    
@bot.on(events.callbackquery.CallbackQuery(data="sett"))
async def sett(event):    
    Drone = event.client                    
    button = await event.get_message()
    msg = await button.get_reply_message() 
    await event.delete()
    async with Drone.conversation(event.chat_id) as conv: 
        xx = await conv.send_message("Send me any image for thumbnail as a `reply` to this message.")
        x = await conv.get_reply()
        if not x.media:
            xx.edit("No media found.")
        mime = x.file.mime_type
        if not 'png' in mime:
            if not 'jpg' in mime:
                if not 'jpeg' in mime:
                    return await xx.edit("No image found.")
        await xx.delete()
        t = await event.client.send_message(event.chat_id, 'Trying.')
        path = await event.client.download_media(x.media)
        if os.path.exists(f'{event.sender_id}.jpg'):
            os.remove(f'{event.sender_id}.jpg')
        os.rename(path, f'./{event.sender_id}.jpg')
        await t.edit("Temporary thumbnail saved!")
        
@bot.on(events.callbackquery.CallbackQuery(data="remt"))
async def remt(event):  
    Drone = event.client            
    await event.edit('Trying.')
    try:
        os.remove(f'{event.sender_id}.jpg')
        await event.edit('Removed!')
    except Exception:
        await event.edit("No thumbnail saved.")                        
    
   
@bot.on(events.callbackquery.CallbackQuery(data="login"))
async def lin(event):
    Drone = event.client
    button = await event.get_message()
    msg = await button.get_reply_message()  
    await event.delete()
    number = 0
    otp = 0
    session = ""
    passcode = ""
    async with Drone.conversation(event.chat_id) as conv: 
        try:
            xx = await conv.send_message("Send me your contact number with country code(eg +1 or +91) to login.")
            contact = await conv.get_response()
            print(contact.text) 
            number = ' '.join(str(contact.text))
        except Exception as e: 
            print(e)
            return await xx.edit("An error occured while waiting for the response.")
        client = Client("my_account", api_id=15329040, api_hash="9aa858bf18bfeb435f8117760dfcfc8d")
        try:
            await client.connect()
        except ConnectionError:
            await client.disconnect()
            await client.connect()
        code_alert = await conv.send_message("Sending code...")
        try:
            code = await client.send_code(number)
            await asyncio.sleep(1)
        except FloodWait as e:
            await conv.send_message(f"Can't send code, you have Floodwait of {e.x} Seconds.")
            return
        except Exception as e:
            print(e)
            await conv.send_message(f"**Error**: {str(e)}")
            return
        try:
            await code_alert.delete()
            ask_code = await conv.send_message(otp_text)  
            otp_ = await conv.get_response()
            otp = otp_.text
        except Exception as e: 
            print(e)
            return await ask_code.edit("An error occured while waiting for the response.")
        try:
            await client.sign_in(number, code.phone_code_hash, phone_code=' '.join(str(otp)))
        except PhoneCodeInvalid:
            await conv.send_message("Invalid Code, try again.")
            return
        except PhoneCodeExpired:
            await conv.send_message("Code has expired, try again.")
            return
        except SessionPasswordNeeded:
            try:
                xz = await conv.send_message("Send your Two-Step Verification password.") 
                z = await conv.get_response()
                passcode = z.text
            except Exception as e: 
                print(e)
                return await xz.edit("An error occured while waiting for the response.")
            try:
                await client.check_password(passcode)
            except Exception as e:
                await conv.send_message(f"**ERROR:** {str(e)}")
                return
        except Exception as e:
            await conv.send_message(f"**ERROR:** {str(e)}")
            return
        try:
            session = await client.export_session_string()
        except Exception as e:
            await conv.send_message(f"**ERROR:** {str(e)}")
            return
        await login(event.sender_id, API_ID, API_HASH, session) 
        await Drone.send_message(event.chat_id, "Login credentials saved.")
        await client.disconnect()
        
@bot.on(events.callbackquery.CallbackQuery(data="logout"))
async def out(event):
    await event.edit("Trying to logout.")
    await logout(event.sender_id)
    await event.edit('successfully Logged out.')
    
@bot.on(events.callbackquery.CallbackQuery(data="startbot"))
async def stb(event):
    await event.edit("Trying to start.")
    MONGODB_URI = config("MONGODB_URI", default=None)
    db = Database(MONGODB_URI, 'saverestricted')
    i, h, s = await db.get_credentials(event.sender_id)
    if i and h and s is not None:
        try:
            userbot = Client(
                session_name=s, 
                api_hash=h,
                api_id=int(i))
            await userbot.start()
            await idle()
            await event.edit("Started!")
        except ValueError:
            return await event.edit("INVALID API_ID: Logout and Login back with correct `API_ID`")
        except Exception as e:
            print(e)
            if 'Client is already connected' in str(e):
                return await event.edit("Already running.")
            else:
                return await event.edit(f"Error: {str(e)}")
    else:
        return await event.edit("Your login credentials not found.")
    
@bot.on(events.callbackquery.CallbackQuery(data="stopbot"))
async def spb(event):   
    MONGODB_URI = config("MONGODB_URI", default=None)
    db = Database(MONGODB_URI, 'saverestricted')
    i, h, s = await db.get_credentials(event.sender_id)
    if i and h and s is not None:
        try:
            userbot = Client(
                session_name=s, 
                api_hash=h,
                api_id=int(i))
            await userbot.stop()
            await event.edit("Bot stopped!")
        except ValueError:
            return await event.edit("INVALID API_ID: Logout and Login back with correct `API_ID`")
        except Exception as e:
            return await event.edit(f"Error: {str(e)}")
    else:
        return await event.edit("Your login credentials not found.")
   
@bot.on(events.callbackquery.CallbackQuery(data="help"))
async def help(event):
    await event.edit(ht, link_preview=False, buttons=[[Button.inline("BACK", data="menu")]])
    
@bot.on(events.callbackquery.CallbackQuery(data="menu"))
async def back(event):
    await event.edit(st, 
                      buttons=[
                              [Button.inline("SET THUMB", data="sett"),
                               Button.inline("REM THUMB", data="remt")],
                              [Button.inline("LOG IN", data="login"),
                               Button.inline("LOG OUT", data="logout")],
                              [Button.inline("HELP", data="help"),
                               Button.url("SOURCE", url="github.com/vasusen-code/saverestrictedcontentbot")],
                              ])
    
    
    
    
    
