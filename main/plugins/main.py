# Github.com/Vasusen-code

from .. import bot as Drone, FORCESUB

from main.plugins.helpers import get_link, force_sub, set_timer
from main.Database.database import db
from main.plugins.pyroplug import get_msg
from main.plugins.batch import batch_link

from pyrogram import Client, filters, types

proccess = 0
     
errorC = """Error: Couldn't start client by Login credentials, Please logout and login again."""

@Drone.on_message(filters=filters.private & filters.incoming, group=2)
async def clone(client, message: types.Message):
    if batch_link:
        return
    user_id = message.from_user.id

    try:
        link = get_link(message.text)
        if not link:
            return
    except TypeError:
        return

    emoji = await message.reply("🔗")

    f, u = await force_sub(client, FORCESUB[0], user_id)
    if f:
        await emoji.delete()
        return await message.reply(f"⚠️ To use this bot you must **join** all below channels\n\n@{FORCESUB[0]}\n@{FORCESUB[1]}")
    f, u = await force_sub(client, FORCESUB[1], user_id)
    if f:
        await emoji.delete()
        return await message.reply(f"⚠️ To use this bot you must **join** all below channels\n\n@{FORCESUB[0]}\n@{FORCESUB[1]}")
    
    count = await db.get_trial_count(user_id)
    if count == 50:
        await emoji.delete()
        await message.reply("⚠️ You have completed your trial of 50 links, please proceed to buy a paid plan from @DroneBOTs")
        n = await db.check_number(user_id)
        if n:
            await db.black_list_number(user_id)
        return
    
    n = await db.check_number(user_id)
    if not n:
        await emoji.delete()
        return await message.reply("⚠️ Trials on this number is already over, buy premium subscription from @DroneBOTs")
    if proccess > 20:
        await emoji.delete()
        return await message.reply("⚠️ Bot is overloaded with 20/20 proccesses, please wait or buy premium from @DroneBots")
    await emoji.delete()

    edit = await message.reply("Processing!")
    if (await db.get_process(user_id))["process"] == True:
        return await edit.edit("❌ Please don't spam links, wait until ongoing process is done.")
    
    timer = 120
    to = await db.get_chat(user_id)
    if to == None:
        to = user_id
    if 't.me/+' in link:
        return await edit.edit("Login & Join yourself manually.")
    if 't.me' in link:
        userbot = ""
        i, h, s = await db.get_credentials(user_id)
        if s:
            try:
                userbot = Client("saverestricted", session_string=s, api_hash=h, api_id=int(i))     
                await userbot.start()
            except Exception as e:
                print(e)
                return await edit.edit(errorC)
        else:
            return await edit.edit("⚠️ Your login credentials not found.")
        await db.update_process(user_id)
        try: 
            await get_msg(userbot, client, user_id, to, edit, link, i=0, plan="basic")
            await userbot.stop()
        except Exception as e:
            print(e)
            pass
        await set_timer(client, user_id, timer) 
