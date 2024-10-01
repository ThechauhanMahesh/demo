#Github.com/Vasusen-code
import logging
import subprocess
import shlex
import json
from datetime import timedelta
from datetime import date
from datetime import datetime as dt
import asyncio, subprocess, re, os, time
import uuid
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait, InviteHashInvalid, InviteHashExpired, UserAlreadyParticipant, FloodPremiumWait
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid, PeerIdInvalid
from pyrogram.errors import UserNotParticipant
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from main.plugins.progress import progress_for_pyrogram
from main.Database.database import db
from main import DL_DIR, CustomBot

def delete_file(file):
    try:
        os.remove(file)
        if os.path.isfile(file):
            os.remove(file)
    except:
        pass

def rreplace(s, old, new):
    return s[::-1].replace(old[::-1], new[::-1], 1)[::-1]

def build_caption(plan, caption, caption_data):
    if plan == "pro":
        action = caption_data["action"]
        if caption is not None:
            new_caption = ""
            if action is not None:
                string = caption_data["string"]
                if action == "add":
                    new_caption = caption + f"\n\n{string}"
                elif action == "delete":
                    new_caption = caption.replace(string, "")
                elif action == "replace":
                    new_caption = caption.replace(string["d"], string["a"])
                caption = new_caption
        elif action == "add":
            caption = caption_data["string"] or ""
    return caption

# TG Link extractor -----------------------------------------------------------------------------------
def extract_tg_link(url):
    if not isinstance(url, str):
        logging.error(f"URL must be a string, {url} given.")
        return None, None
    pattern = r"^(?:(?:https|tg):\/\/)?(?:www\.)?(?:t\.me\/)?(?:(?:c\/(\d+))|(?:b\/)?(\w+)|(?:openmessage\?user_id\=(\d+)))(?:\/|&message_id\=)(\d+)(?:\/(\d+))?(\?single)?$"
    if match := re.search(pattern, url.strip()):
        chat_id = None
        msg_id = int(match.group(4))
        if match.group(1):
            chat_id = int("-100" + match.group(1))
        elif match.group(2):
            chat_id = match.group(2)
        elif match.group(3):
            chat_id = int(match.group(3))
        if match.group(5):
            msg_id = int(match.group(5))
        if chat_id and msg_id:
            return chat_id, msg_id
    return None, None

# Subscription ----------------------------------------------------------------------------------

async def check_subscription(id):
    try: 
        doe = (await db.get_data(id))["doe"]
    except Exception:
        return
    if not doe:
        return
    z = doe.split("-")
    e = int(z[0] + z[1] + z[2])
    x = str(dt.now()).split(" ")[0]
    w = x.split("-")
    today = int(w[0] + w[1] + w[2])
    if today > e:
        await db.rem_data(id)
    else:
        return 

async def set_subscription(user_id, dos, days, plan):
    if not dos:
        x = str(dt.now()).split(" ")[0]
        dos_ = x.split("-")
    else:
        dos_ = dos.split("-")
    today = date(int(dos_[0]), int(dos_[1]), int(dos_[2]))
    expiry_date = today + timedelta(days=days)
    data = {"dos":str(today), "doe":str(expiry_date), "plan":plan}
    await db.update_data(user_id, data)

#Multi client-------------------------------------------------------------------------------------------------------------

async def login_credentials(sender, i, h, s):
    await db.update_api_id(sender, i)
    await db.update_api_hash(sender, h)
    await db.update_session(sender, s)
    
async def logout_credentials(sender):
    await db.rem_api_id(sender)
    await db.rem_api_hash(sender)
    await db.rem_session(sender)

#Anti-Spam---------------------------------------------------------------------------------------------------------------

#Set timer to avoid spam
async def set_timer(bot, sender, t):
    await bot.send_message(sender, f'You can start a new process again after {t} seconds\n\nBuy premium from @DroneBots to avoid limits. ✅')
    await asyncio.sleep(int(t))
    await db.rem_process(sender)

#Forcesub -----------------------------------------------------------------------------------

async def force_sub(client: CustomBot, channel, id):
    s, r = False, None
    try:
        # In Pyrogram, IDs should be directly usable, so ensure 'id' is integer if not handled externally.
        x = await client.get_chat_member(channel, id)
        
        # Check if the participant has left the channel
        if x.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]:
            s, r = True, f"To use this bot you must JOIN @{channel}"
        else:
            s, r = False, None
    except UserNotParticipant:
        s, r = True, f"To use this bot you must JOIN @{channel}"
    except Exception as e:
        s, r = True, f"ERROR: Add in ForceSub channel, or check your channel id. Details: {str(e)}"
    return s, r


#Join private chat-------------------------------------------------------------------------------------------------------------

async def join(client: CustomBot, invite_link):
    try:
        await client.join_chat(invite_link)
        return "Successfully joined the Channel"
    except UserAlreadyParticipant:
        return "User is already a participant."
    except (InviteHashInvalid, InviteHashExpired):
        return "Could not join. Maybe your link is expired or Invalid."
    except (FloodWait, FloodPremiumWait):
        return "Too many requests, try again later."
    except Exception as e:
        print(e)
        return "Could not join, try joining manually."
        
#Regex---------------------------------------------------------------------------------------------------------------
#to get the url from event

def get_link(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)
    try:
        return link if (link := [x[0] for x in url][0]) else False
    except Exception:
        return False
    
# screenshot ---------------------------------------------------------------------------------------------------------------
    
def hhmmss(seconds):
    x = time.strftime('%H:%M:%S',time.gmtime(seconds))
    return x

async def screenshot(video, duration):
    # if os.path.exists(f'{sender}.jpg'):
    #     return f'{sender}.jpg'
    time_stamp = hhmmss(int(duration)/2)
    out = dt.now().isoformat("_", "seconds") + ".jpg"
    cmd = ["ffmpeg",
           "-ss",
           f"{time_stamp}", 
           "-i",
           f"{video}",
           "-frames:v",
           "1", 
           f"{out}",
           "-y"
          ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    x = stderr.decode().strip()
    y = stdout.decode().strip()
    if os.path.isfile(out):
        return out
    else:
        None       

# metadata ---------------------------------------------------------------------------------------------------------------
 
# function to find the metadata of the input video file
async def findVideoMetadata(pathToInputVideo):

    height, width, duration_seconds = 90, 90, 0

    try:
        metadata = extractMetadata(createParser(pathToInputVideo))
        if metadata and metadata.has("duration"):
            duration_seconds = metadata.get("duration").seconds
            try:
                thumb = await screenshot(pathToInputVideo, duration_seconds)
            except:
                thumb = None
            if thumb != None:
                metadata = extractMetadata(createParser(thumb))
                if metadata and metadata.has("width"):
                    width = metadata.get("width")
                if metadata and metadata.has("height"):
                    height = metadata.get("height")
        else:
            cmd = "ffprobe -v quiet -print_format json -show_streams"
            args = shlex.split(cmd)
            args.append(pathToInputVideo)
            # run the ffprobe process, decode stdout into utf-8 & convert to JSON
            ffprobeOutput = subprocess.check_output(args).decode('utf-8')
            ffprobeOutput = json.loads(ffprobeOutput)

            # find height and width
            height = ffprobeOutput['streams'][0]['height']
            width = ffprobeOutput['streams'][0]['width']

            # find duration
            out = subprocess.check_output(["ffprobe", "-v", "quiet", "-show_format", "-print_format", "json", pathToInputVideo])
            ffprobe_data = json.loads(out)
            duration_seconds = float(ffprobe_data["format"]["duration"])
    except:
        return 90, 90, 0

    return int(height), int(width), int(duration_seconds)

def extract_file_name(msg: Message):
    def get_file_ext():
        ext = None
        if msg.media == MessageMediaType.DOCUMENT:
            ext = ".zip"
        elif msg.media == MessageMediaType.VIDEO:
            ext = ".mp4"
        elif msg.media == MessageMediaType.AUDIO:
            ext = ".mp3"
        elif msg.media == MessageMediaType.VOICE:
            ext = ".ogg"
        elif msg.media == MessageMediaType.PHOTO:
            ext = ".jpg"
        else:
            ext = ".mp4"
        return ext
    media = msg.document or msg.video or msg.audio or msg.voice or msg.photo or msg.animation or msg.sticker or msg.video_note
    if media:
        file_name = getattr(media, "file_name", str(uuid.uuid4().hex) + (get_file_ext() or ".mp4"))
        return file_name

# download ---------------------------------------------------------------------------------------------------------------

async def download(client:CustomBot, msg, editable_msg, file_name=None):
    # if not file_name:
    #     file_name = extract_file_name(msg) or str(uuid.uuid4().hex) + ".mp4"
    # if file_name:
    #     file_name = os.path.basename(file_name).replace(os.sep, "-")
    #     file_name = os.path.join("downloads", file_name)
    file = None
    try:
        dl_dir = os.path.join(DL_DIR, str(client.me.id), os.sep)
        file = await client.download_media(
                msg,
                file_name=dl_dir,
                progress=progress_for_pyrogram,
                progress_args=(
                    client,
                    "**🔻 DOWNLOADING:**\n",
                    editable_msg,
                    time.time()
                )
            )
        return True, file
    except FileNotFoundError:
        if file:
            delete_file(file)
        return await download(client, msg, editable_msg, file_name=file_name)
    except (ChannelInvalid, ChatInvalid, ChatIdInvalid, PeerIdInvalid):
        return False, "⚠️ Invalid link, check your link and try again."
    except ChannelBanned:
        return False, "⚠️ You are banned from this chat"
    except ChannelPrivate:
        return False, "⚠️ You are not joined in this channel"
    except UserNotParticipant:
        return False, "⚠️ You are not joined in this channel"
    except Exception as e:
        if "This message doesn't contain any downloadable" in str(e):
            return False, "⚠️ This message doesn't contain any downloadable media."
        else:
            return False, str(e)

# upload ---------------------------------------------------------------------------------------------------------------
  
async def upload(client:CustomBot, file, to, msg, editable_msg, thumb_path=None, caption=None):
    try:
        if msg.media==MessageMediaType.VIDEO_NOTE:
            height, width, duration = await findVideoMetadata(file)
            print(f'd: {duration}, w: {width}, h:{height}')
            try:
                if not thumb_path:
                    thumb_path = await screenshot(file, duration)
            except Exception:
                thumb_path = None
            sent = await client.send_video_note(
                chat_id=to,
                video_note=file,
                length=height, duration=duration, 
                thumb=thumb_path,
                progress=progress_for_pyrogram,
                progress_args=(
                    client,
                    '**🔺 UPLOADING:**\n',
                    editable_msg,
                    time.time()
                )
            )
        elif msg.media==MessageMediaType.VIDEO and msg.video.mime_type in ["video/mp4", "video/x-matroska"]:
            height, width, duration = await findVideoMetadata(file)
            print(f'd: {duration}, w: {width}, h:{height}')
            try:
                if not thumb_path:
                    thumb_path = await screenshot(file, duration)
            except Exception:
                thumb_path = None
            sent = await client.send_video(
                chat_id=to,
                video=file,
                caption=caption,
                supports_streaming=True,
                height=height, width=width, duration=duration, 
                thumb=thumb_path,
                progress=progress_for_pyrogram,
                progress_args=(
                    client,
                    '**🔺 UPLOADING:**\n',
                    editable_msg,
                    time.time()
                )
            )
        elif msg.media==MessageMediaType.VOICE:
            sent = await client.send_voice(to, file, caption=caption)
        elif msg.media==MessageMediaType.PHOTO:
            try:
                await editable_msg.edit("🔺 Uploading photo...")
            except:
                pass
            sent = await client.send_photo(to, file, caption=caption)
        else:
            sent = await client.send_document(
                to,
                file, 
                caption=caption,
                thumb=thumb_path,
                progress=progress_for_pyrogram,
                progress_args=(
                    client,
                    '**🔺 UPLOADING:**\n',
                    editable_msg,
                    time.time()
                )
            )
        delete_file(file)
        if thumb_path:
            delete_file(thumb_path)
        try:
            await editable_msg.edit("Finalizing the upload...")
        except:
            pass
        return True, sent
    except (ChannelInvalid, ChatInvalid) as e:
        logging.exception(e)
        False, "⚠️ You are not joined this channel/chat with the logged in account"
    except (ChatIdInvalid, PeerIdInvalid) as e:
        logging.exception(e)
        return False, "⚠️ Check your setchat ID or add bot as admin in your setchat channel."
    except Exception as e:
        logging.exception(e)
        if "'NoneType' object has no attribute 'name'" in str(e):
            return True, None
        if "size equals" in str(e):
            await asyncio.sleep(60)
            try:
                os.remove(file)
            except:
                pass
            return False, None
        elif "messages.SendMedia" in str(e) \
        or "SaveBigFilePartRequest" in str(e) \
        or "SendMediaRequest" in str(e):
            try:
                sent = await client.send_document(
                    to,
                    file, 
                    caption=caption,
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        '**🔺 UPLOADING:**\n',
                        editable_msg,
                        time.time()
                    )
                )
                delete_file(file)
                if thumb_path:
                    delete_file(thumb_path)
                return True, sent
            except Exception as e:
                return False, str(e)
        return False, str(e)
    return False, None
