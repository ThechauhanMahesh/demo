#ChauhanMahesh/Vasusen/DroneBots/COL

from pyrogram import Client
from pyromod import listen
import logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
"""
muk : 5287338189:AAFAtkAu7hyActQBoK6XCmhKGAkPIZQ1e8E
mine : 6125089272:AAEDF254YhMbUK5hhl0yFbEQTqlhgA3W0jc
"""
# variables
API_ID = 2992000
API_HASH = "235b12e862d71234ea222082052822fd"
BOT_TOKEN = "6125089272:AAEDF254YhMbUK5hhl0yFbEQTqlhgA3W0jc"
FORCESUB = ["Save_Restricted_Message", "Save_Restricted_Content_1"]
MONGODB_URI = "mongodb+srv://thechauhanmahesh:XgbFpSEe3pM9P45z@cluster0.mkaomd0.mongodb.net"
AUTH_USERS = 1807573686

help_text = """Help:

**FOR PUBLIC CHANNEL:**
- Send me direct link of message. 

**FOR PRIVATE CHANNEL:**
- Login 
- Then send Link of message of any channel you've joined.

#FAQ 

- If bot says “Have you joined the channel?” Then just login again in bot and try.

- If bot says “Please don't spam links, wait until ongoing process is done.” then send /free command in bot and try after 10 minutes. 

- if bot says “Login credentials not found” the just login again

- If bot shows error containing “AUTH_KEY_DUPLICATED” in it then login again.

- if you batch is stuck then use /cancel 

#Note : Don't use the /free command unnecessarily.
"""

otp_text = """An OTP has been sent to your number. 

Please send the OTP with space, example: `1 2 3 4 5`."""

bot = Client(
    "PyrogamBot", 
    api_hash=API_HASH, 
    api_id=API_ID, 
    bot_token=BOT_TOKEN,
    workers=343
    ) # pyrogram bot

# try:
#     bot.start()
# except Exception as e:
#     print(e)
#     sys.exit()

