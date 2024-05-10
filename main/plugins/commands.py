# Github.com/Vasusen-code

import os, asyncio
from .. import bot as Drone, API_ID, API_HASH, help_text as ht, otp_text, AUTH_USERS

from pyromod.exceptions import ListenerTimeout
from pyrogram import Client, filters, types
from pyrogram.errors import SessionPasswordNeeded, FloodWait, PhoneCodeInvalid, PhoneCodeExpired 

from main.plugins.helpers import login_credentials, logout_credentials
from main.Database.database import db

APIID = [API_ID, 29841594]
APIHASH = [API_HASH, "1674d13f3308faa1479b445cdbaaad2b"]

@Drone.on_message(filters=filters.private & filters.incoming, group=1)
async def incomming(_, message: types.Message):
    user_id = message.from_user.id
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id)
        await message.reply("https://t.me/Save_restricted_message/3")

@Drone.on_message(filters=filters.command('setchat') & filters.incoming)
async def start(_, message: types.Message):
    return await message.reply("⚠️ Only for paid users, check @DroneBOTs")

@Drone.on_message(filters=filters.command('remchat') & filters.incoming)
async def start(_, message: types.Message):
    return await message.reply("⚠️ Only for paid users, check @DroneBOTs")

@Drone.on_message(filters=filters.command('start') & filters.incoming)
async def start(_, message: types.Message):
    await message.reply("Send me **link** of any **public** channel message to clone it here 🔗, For **private** channel message, First **/login** then send any **message link** from your chat ✅.\n\n**SUPPORT:** @TeamDrone\n**DEV:** @MaheshChauhan") 

@Drone.on_message(filters=filters.command('login') & filters.incoming)
async def login(_, message: types.Message):
    number, otp, code = 0, 0, 0
    session, passcode, ai, ah= None, None, None, None
    user_id = message.from_user.id

    i, h, s = await db.get_credentials(user_id)
    if s:
        return await message.reply("⚠️ You are already logged in.")

    try:
        contact = await Drone.ask(chat_id=user_id, text="Send me your contact number with country code(eg +1 or +91) to login.", filters=filters.text, timeout=60)
        number = ' '.join(str(contact.text))
        if "-" in number:
            number = '-'.join(number)
        numbers_logged_in = await db.get_numbers()
        if number in numbers_logged_in:
            return await message.reply("❌ This number is already in use by another user.")
        
        code_alert = await message.reply("Sending code...")

        ai = APIID[0]
        ah = APIHASH[0]
        client = Client(f"{user_id}_account", api_id=ai, api_hash=ah, in_memory=True)
        try:
            await client.connect()
        except ConnectionError:
            await client.disconnect()
            await client.connect()
        try:
            code = await client.send_code(number)
            await asyncio.sleep(1)
        except FloodWait:
            await client.disconnect()
            client = Client("my_account", api_id=APIID[-1], api_hash=APIHASH[-1])
            ai = APIID[-1]
            ah = APIHASH[-1]
            try:
                await client.connect()
            except ConnectionError:
                await client.disconnect()
                await client.connect()
            try:
                code = await client.send_code(number)
                await asyncio.sleep(1)
            except FloodWait as e:
                await code_alert.edit(f"Can't send code, you have Floodwait of {e.x} Seconds.")
                return
            except Exception as e:
                print(e)
                await code_alert.edit(f"**Error**: {str(e)}")
                return
            await code_alert.delete()

        ask_code = await Drone.ask(chat_id=user_id, text=otp_text, filters=filters.text, timeout=60)
        otp = ask_code.text
        try:
            await client.sign_in(number, code.phone_code_hash, phone_code=' '.join(str(otp)))
        except PhoneCodeInvalid:
            await message.reply("Invalid Code, try again.")
            return
        except PhoneCodeExpired:
            await message.reply("Code has expired, try again.")
            return
        except SessionPasswordNeeded:
            two_step = await Drone.ask(chat_id=user_id, text="Send your Two-Step Verification password.", filters=filters.text, timeout=60)
            passcode = two_step.text
            try:
                await client.check_password(passcode)
            except Exception as e:
                await message.reply(f"**ERROR:** {str(e)}")
                return
        except Exception as e:
            await message.reply(f"**ERROR:** {str(e)}")
            return
    except ListenerTimeout:
        return await message.reply("You took too long to respond.")
    try:
        session = await client.export_session_string()
    except Exception as e:
        await message.reply(f"**ERROR:** {str(e)}")
        return
    
    await login_credentials(user_id, ai, ah, session) 
    await message.reply("✅ Login credentials saved.\n\n⚠️ click on 'yes its me' when telegram asks if is it you who logged in.")
    await client.disconnect()
    await db.update_number(user_id, number)

@Drone.on_message(filters=filters.command('logout') & filters.incoming)
async def logout(_, message: types.Message):
    edit = await message.reply("Trying to logout.")
    await logout_credentials(message.from_user.id)
    await db.rem_number(message.from_user.id)
    await edit.edit('✅ successfully Logged out.')

@Drone.on_message(filters=filters.command('help') & filters.incoming)
async def help(_, message: types.Message):
    await message.reply(ht)

@Drone.on_message(filters=filters.command('setthumb') & filters.incoming)
async def setthumb(client, message: types.Message):   
    user_id = message.from_user.id
    try:
        image = await Drone.ask(chat_id=user_id, text="Send me any image for thumbnail.", filters=filters.photo, timeout=60)   
    except ListenerTimeout:
        return await message.reply("You took too long to respond.")      
    edit = await message.reply("Trying to download..")
    path = await client.download_media(image)
    if os.path.exists(f'{user_id}.jpg'):
        os.remove(f'{user_id}.jpg')
    os.rename(path, f'./{user_id}.jpg')
    await edit.edit("✅ Temporary thumbnail saved!")

@Drone.on_message(filters=filters.command('remthumb') & filters.incoming)
async def remthumb(_, message: types.Message):             
    edit = await message.reply('Trying.')
    try:
        os.remove(f'{message.from_user.id}.jpg')
        await edit.edit('✅ Removed!')
    except Exception:
        await edit.edit("No thumbnail was saved.") 
