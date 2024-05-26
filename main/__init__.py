#ChauhanMahesh/Vasusen/DroneBots/COL

from pyrogram import Client
from pyromod import listen
import logging, sys, pymongo

from pyrogram.raw.types import KeyboardButtonRequestPeer

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

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


"""
me : 6710941011:AAFVG83NRSnaohlnYR_KCM1MtnWPnsDbiuY
m1 : 6633102102:AAEZLOFpQUfOHvNgBdAlJ7H52hnOXaUMpfY
"""

# variables
API_ID = 2992000
API_HASH = "235b12e862d71234ea222082052822fd"
BOT_TOKEN = "6710941011:AAFVG83NRSnaohlnYR_KCM1MtnWPnsDbiuY"
FORCESUB = int("-1001711957758")
ACCESS = int("-1001879806908")
MONGODB_URI = "mongodb+srv://thechauhanmahesh:XgbFpSEe3pM9P45z@cluster0.mkaomd0.mongodb.net"
AUTH_USERS = 1807573686
SESSION_NAME = "PremiumSRCB2"

client = pymongo.MongoClient(MONGODB_URI)
db = client[SESSION_NAME] 
collection = db["users"]  
process = {"process":{"process":False, "batch":False}}
collection.update_many({}, {"$set":process})
print("All users have been set free.")

bot = Client(
    "PyrogamBot", 
    api_hash=API_HASH, 
    api_id=API_ID, 
    bot_token=BOT_TOKEN,
    workers=343
    ) # pyrogram bot


class RequestPeer:
    def __init__(self, text, button_id, peer_type):
        self.text = text
        self.button_id = button_id
        self.peer_type = peer_type

    def write(self):
        return KeyboardButtonRequestPeer(
            text=self.text, button_id=self.button_id, peer_type=self.peer_type
        )
