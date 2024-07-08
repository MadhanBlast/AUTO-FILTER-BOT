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

# Set up logging (optional)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

@Client.on_callback_query(filters.regex('cancel'))
async def cancel(bot, update):
    try:
        await update.message.delete()
    except Exception as e:
        logger.error(f"Error while deleting message: {e}")

@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):
    try:
        type = update.data.split("_")[1]
        new_name = update.message.text
        new_filename = new_name.split(":-")[1]
        file = update.message.reply_to_message
        file_path = f"downloads/{new_filename}"
        ms = await update.message.edit("⚠️__**Please wait...**__\n\n__Downloading file to my server...__")
        c_time = time.time()
        
        try:
            # Download the file
            path = await bot.download_media(
                message=file,
                file_name=file_path,
                progress=progress_for_pyrogram,
                progress_args=("⚠️ Please wait, file download in progress...", ms, c_time)
            )
        except Exception as e:
            await ms.edit(f"Error downloading file: {e}")
            return
        
        # Process metadata if available
        duration = 0
        try:
            metadata = extractMetadata(createParser(file_path))
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")
        
        # Prepare caption based on user preferences
        user_id = int(update.message.chat.id)
        media = getattr(file, file.media.value)
        filesize = humanize.naturalsize(media.file_size)
        c_caption = await db.get_caption(update.message.chat.id)
        c_thumb = await db.get_thumbnail(update.message.chat.id)

        if c_caption:
            try:
                caption = c_caption.format(filename=new_filename, filesize=humanize.naturalsize(media.file_size), duration=convert(duration))
            except Exception as e:
                await ms.edit(text=f"Error in caption: {e}")
                return
        else:
            caption = f"**{new_filename}**"

        # Handle thumbnail if available
        ph_path = None
        if media.thumbs or c_thumb:
            if c_thumb:
                ph_path = await bot.download_media(c_thumb)
            else:
                ph_path = await bot.download_media(media.thumbs[0].file_id)
                Image.open(ph_path).convert("RGB").save(ph_path)
                img = Image.open(ph_path)
                img.resize((320, 320))
                img.save(ph_path, "JPEG")

        # Send the file to the user
        await ms.edit("⚠️__**Please wait...**__\n\n__Processing file upload....__")
        c_time = time.time()
        
        try:
            if type == "document":
                await bot.send_document(
                    update.message.chat.id,
                    document=file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("⚠️__**Please wait...**__\n__Processing file upload....__", ms, c_time)
                )
            elif type == "video":
                await bot.send_video(
                    update.message.chat.id,
                    video=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("⚠️__**Please wait...**__\n__Processing file upload....__", ms, c_time)
                )
            elif type == "audio":
                await bot.send_audio(
                    update.message.chat.id,
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
client.run()

		    
