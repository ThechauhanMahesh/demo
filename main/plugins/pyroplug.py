# Github.com/Vasusen-code

import logging
import os 
from main.plugins.helpers import build_caption, download, extract_tg_link, upload
from main.Database.database import db
from main import DUMP_CHANNEL
from pyrogram.enums import MessageMediaType, ChatType
from pyrogram.errors import PeerIdInvalid, MessageEmpty, MessageIdInvalid, ChannelInvalid
from pyrogram import Client

def thumbnail(sender):
    return f'{sender}.jpg' if os.path.exists(f'{sender}.jpg') else None
      
async def get_msg(userbot, client: Client, sender, to, editable_msg, msg_link, caption_data, retry=0, plan="basic", is_batch=False):
    if retry >= 3:
        return await editable_msg.edit(f"❌ Failed to save: `{msg_link}`\n\nError: Maximum retries exceeded.")

    file, caption, thumb_path = None, None, thumbnail(sender)

    if "?single" in msg_link:
        msg_link = msg_link.split("?single")[0]

    chat, msg_id = extract_tg_link(msg_link)
    
    # if cache_file := await db.get_cache(msg_id, chat):
    #     caption = build_caption(plan, caption=cache_file["caption"] or "", caption_data=caption_data)
    #     await client.copy_message(chat_id=to, from_chat_id=DUMP_CHANNEL, message_id=cache_file["msg_id"], caption=caption)
    #     await editable_msg.delete()
    #     return

    if chat and msg_id:
        try:
            try:
                msg = await userbot.get_messages(chat, msg_id)
                if msg.empty:
                    raise Exception("Message deleted or not exist.")
            except (KeyError, PeerIdInvalid):
                raise Exception("Chat not found or you are not a member of the chat.")
            except (MessageEmpty, MessageIdInvalid):
                raise Exception("Message not found.")
            except Exception as e:
                if is_batch:
                    return await editable_msg.delete()
                return await editable_msg.edit(f'❌ Failed to save: `{msg_link}`\n\nError: {str(e)}')
            if (
                msg.media
                and msg.media == MessageMediaType.WEB_PAGE
                or not msg.media
                and msg.text
            ):
                await editable_msg.edit(text="Cloning...")
                await userbot.send_message(to, msg.text.markdown)
                await editable_msg.delete()
                return
            elif msg.media:
                caption = build_caption(plan, msg.caption, caption_data)
                if msg.chat.type == ChatType.CHANNEL and getattr(msg.chat, "username", None):
                    await editable_msg.edit("Cloning..")
                    #await msg.copy(chat_id=to, caption=caption)
                    await client.copy_message(chat_id=to, from_chat_id=msg.chat.username, message_id=msg.id, caption=caption)
                    return await editable_msg.delete()
                downloaded, update = await download(userbot, msg, editable_msg)
                if not downloaded:
                    await editable_msg.edit(text=f"❌ Failed to save: `{msg_link}`\n\nError: {update}")
                    return
                else:
                    file = update
            else:
                if is_batch:
                    return await editable_msg.delete()
                return await editable_msg.edit(f'❌ Failed to save: `{msg_link}`\n\nError: Invalid link.')

            await editable_msg.edit("Preparing to upload...")

            if file is None:
                return await editable_msg.edit(f'❌ Failed to save: `{msg_link}`\n\nThis link is not downloadble.')

            if os.path.getsize(file) > 2097152000:
                if plan != "pro":
                    return await editable_msg.edit("Buy pro plan and telegram premium to upload file size over 2Gb.")
                if to == sender:
                    to = client.me.id
                uploaded, update = await upload(userbot, file, to, msg, editable_msg, thumb_path=thumb_path, caption=caption)
            else:
                up_client = client.get_client()
                if not up_client:
                    return await editable_msg.edit("❌ Failed to save: `{msg_link}`\n\nError: No clients available to use.")
                uploaded, update = await upload(up_client["client"], file, DUMP_CHANNEL, msg, editable_msg, thumb_path=thumb_path, caption=caption)
                if uploaded and update:
                    # await db.save_cache(msg_id, chat, update.id, msg.caption.markdown if msg.caption else "")
                    try:
                        await client.copy_message(chat_id=to, from_chat_id=DUMP_CHANNEL, message_id=update.id)
                    except (PeerIdInvalid, ChannelInvalid):
                        return await editable_msg.edit(f"❌ Failed to save: `{msg_link}`\n\nError: Please add me to the channel [{to}]")
                client.release_client(up_client)
            if uploaded:
                await editable_msg.delete()
            elif update:
                return await editable_msg.edit(f"❌ Failed to upload: `{msg_link}`\n\nError: {update}")
            else:
                return await get_msg(userbot, client, sender, to, editable_msg, msg_link, caption_data, retry=retry, plan=plan, is_batch=is_batch)
        except Exception as e:
            logging.exception(e)
            return await editable_msg.edit(f'❌ Failed to save: `{msg_link}`\n\nError: {str(e)}')

        await editable_msg.delete()
    else:
        await editable_msg.edit(f'❌ Failed to save: `{msg_link}`\n\nError: Invalid link.')
