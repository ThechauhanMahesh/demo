import traceback
from typing import Union
from pyrogram import (
    raw,
    utils
)
from pyrogram.types import (
    Message
)

def get_media_file_name(message: Message):
    """
    Pass Message object of audio or document or sticker or video or animation to get file_name.
    """

    media = message.audio or \
            message.document or \
            message.sticker or \
            message.video or \
            message.animation

    if media and media.file_name:
        return media.file_name
    else:
        return None


def get_media_file_size(message: Message):
    """
    Pass Message object of audio or document or photo or sticker or video or animation or voice or video_note to get file_size.
    """

    media = message.audio or \
            message.document or \
            message.photo or \
            message.sticker or \
            message.video or \
            message.animation or \
            message.voice or \
            message.video_note

    if media and media.file_size:
        return media.file_size
    else:
        return None


def get_media_mime_type(message: Message):
    """
    Pass Message object of audio or document or video to get mime_type
    """

    media = message.audio or \
            message.document or \
            message.video
    
    if media and media.mime_type:
        return media.mime_type
    else:
        return None


def get_media_file_id(message: Message):
    """
    Pass Message object of audio or document or photo or sticker or video or animation or voice or video_note to get file_id.
    """

    media = message.audio or \
            message.document or \
            message.photo or \
            message.sticker or \
            message.video or \
            message.animation or \
            message.voice or \
            message.video_note

    if media and media.file_id:
        return media.file_id
    else:
        return None


def get_file_type(message: Message):
    if message.document:
        return "document"
    if message.video:
        return "video"
    if message.audio:
        return "audio"


def get_file_attr(message: Message):

    """
    Combine audio or video or document
    """

    media = message.audio or \
            message.video or \
            message.document

    return media


def get_thumb_file_id(message: Message):
    media = message.audio or \
            message.video or \
            message.document
    if media and media.thumbs:
        return media.thumbs[0].file_id
    else:
        return None

async def big_uploader(
    c,
    sender,
    m: Message,
    file_id: Union[
        "raw.types.InputFileBig",
        "raw.types.InputFile"
    ],
    file_name: str,
    file_size: int,
    edit: Message,
    file_type: str
):
    await edit.edit("Sending to you ...")
    caption = ""
    if m.caption is not None:
        caption = m.caption
    parse_mode = "Markdown"
    if file_type == "video":
        ttl_seconds = None
        supports_streaming = m.video.supports_streaming \
            if m.supports_streaming \
            else None
        duration = m.video.duration \
            if m.video.duration \
            else 0
        width = m.video.width \
            if m.video.width \
            else 0
        height = m.video.height \
            if m.video.height \
            else 0
        mime_type = m.video.mime_type \
            if m.video.mime_type \
            else "video/mp4"
        thumb = None
        media = raw.types.InputMediaUploadedDocument(
            file=raw.types.InputFile(id=file_id, parts=1, name=file_name),
            mime_type=mime_type,
            ttl_seconds=ttl_seconds,
            thumb=thumb,
            caption=caption,
            attributes=[
                raw.types.DocumentAttributeVideo(
                    supports_streaming=supports_streaming,
                    duration=duration,
                    w=width,
                    h=height
                ),
                raw.types.DocumentAttributeFilename(file_name=file_name)
            ]
        )

    elif file_type == "audio":
        thumb = None
        mime_type = m.audio.mime_type \
            if m.audio.mime_type \
            else "audio/mpeg"
        duration = m.audio.duration \
            if m.audio.duration \
            else None
        performer = m.audio.performer \
            if m.audio.performer \
            else None
        title = m.audio.title \
            if m.audio.title \
            else None

        media = raw.types.InputMediaUploadedDocument(
            mime_type=mime_type,
            file=raw.types.InputFile(id=file_id, parts=1, name=file_name),
            force_file=None,
            thumb=thumb,
            caption=caption,
            attributes=[
                raw.types.DocumentAttributeAudio(
                    duration=duration,
                    performer=performer,
                    title=title
                ),
                raw.types.DocumentAttributeFilename(file_name=file_name)
            ]
        )

    elif file_type == "document":
        thumb = None
        mime_type = get_media_mime_type(m) or "application/zip"

        media = raw.types.InputMediaUploadedDocument(
            mime_type=mime_type,
            file=raw.types.InputFile(id=file_id, parts=1, name=file_name),
            force_file=True,
            caption=caption,
            thumb=thumb,
            attributes=[
                raw.types.DocumentAttributeFilename(file_name=file_name)
            ]
        )

    else:
        return None
    return media

    
