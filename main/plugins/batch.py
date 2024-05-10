#Tg:MaheshChauhan/DroneBots
#Github.com/Vasusen-code

"""
Plugin for both public & private channels!
"""

from .. import bot as Drone

from pyrogram import filters, types

errorC = """Error: Couldn't start client by Login credentials, Please logout and login again."""

batch_link = False

@Drone.on_message(filters=filters.command('cancel') & filters.incoming)
async def cancel(_, message: types.Message):
    return await message.reply("⚠️ Only for paid users, check @DroneBOTs")

@Drone.on_message(filters=filters.command('myplan') & filters.incoming)
async def myplan(_, message: types.Message):
    return await message.reply("⚠️ Only for paid users, check @DroneBOTs")

@Drone.on_message(filters=filters.command('caption') & filters.incoming)
async def caption(_, message: types.Message):
    return await message.reply("⚠️ Only for paid users, check @DroneBOTs")
        
@Drone.on_message(filters=filters.command('batch') & filters.incoming & filters.private)
async def batch(_, message: types.Message):
    return await message.reply("⚠️ Only for paid users, check @DroneBOTs")
