# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram import Client, filters
from pyrogram.types import Message
from database.users_chats_db import db
from plugins.Extra.utils import progress_for_pyrogram, convert, humanbytes
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
import os
import humanize
import time
import logging
from PIL import Image

# Initialize your Pyrogram Client
client = Client("my_bot")

# Set up logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

@client.on_callback_query(filters.regex('cancel'))
async def cancel(bot, update):
    try:
        await update.message.delete()
    except Exception as e:
        logger.error(f"Error while deleting message: {e}")

@client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def handle_media(client, message):
    try:
        logger.info(f"Received message: {message}")

        file = message.document or message.audio or message.video
        filename = file.file_name
        file_path = f"downloads/{filename}"

        logger.info(f"File: {filename}, Size: {humanize.naturalsize(file.file_size)}")

        if file.file_size > 2000 * 1024 * 1024:
            await message.reply_text("Sorry, this bot does not support uploading files larger than 2GB.")
            return

        # Download the file
        ms = await message.reply_text("⚠️__**Please wait...**__\n\n__Downloading file to my server...__")
        c_time = time.time()

        try:
            path = await client.download_media(
                message=file,
                file_name=file_path,
                progress=progress_for_pyrogram,
                progress_args=("⚠️ Please wait, file download in progress...", ms, c_time)
            )
        except Exception as e:
            await ms.edit(f"Error downloading file: {e}")
            return

        logger.info(f"File downloaded to: {path}")

        # Process metadata if available
        duration = 0
        try:
            metadata = extractMetadata(createParser(file_path))
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")

        # Prepare caption based on user preferences
        user_id = int(message.chat.id)
        filesize = humanize.naturalsize(file.file_size)
        c_caption = await db.get_caption(message.chat.id)
        c_thumb = await db.get_thumbnail(message.chat.id)

        if c_caption:
            try:
                caption = c_caption.format(filename=filename, filesize=filesize, duration=convert(duration))
            except Exception as e:
                await ms.edit(text=f"Error in caption: {e}")
                return
        else:
            caption = f"**{filename}**"

        # Handle thumbnail if available
        ph_path = None
        if file.thumbs or c_thumb:
            if c_thumb:
                ph_path = await client.download_media(c_thumb)
            else:
                ph_path = await client.download_media(file.thumbs[0].file_id)
                Image.open(ph_path).convert("RGB").save(ph_path)
                img = Image.open(ph_path)
                img.resize((320, 320))
                img.save(ph_path, "JPEG")

        # Send the file to the user
        await ms.edit("⚠️__**Please wait...**__\n\n__Processing file upload....__")
        c_time = time.time()

        try:
            if message.document:
                await client.send_document(
                    message.chat.id,
                    document=file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("⚠️__**Please wait...**__\n__Processing file upload....__", ms, c_time)
                )
            elif message.video:
                await client.send_video(
                    message.chat.id,
                    video=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("⚠️__**Please wait...**__\n__Processing file upload....__", ms, c_time)
                )
            elif message.audio:
                await client.send_audio(
                    message.chat.id,
                    audio=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("⚠️__**Please wait...**__\n__Processing file upload....__", ms, c_time)
                )
        except Exception as e:
            await ms.edit(f"Error sending file: {e}")
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            return

        await ms.delete()
        os.remove(file_path)
        if ph_path:
            os.remove(ph_path)

    except Exception as e:
        logger.error(f"Error: {e}")

# Start your Pyrogram Client
if __name__ == "__main__":
    client.run()
