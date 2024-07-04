from asyncio import sleep
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from pyrogram.errors import FloodWait
from info import RENAME_MODE
import humanize
import random

@Client.on_message(filters.private & filters.command("rename"))
async def rename_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name  
    if file.file_size > 2000 * 1024 * 1024:
         return await message.reply_text("Sᴏʀʀy Bʀᴏ Tʜɪꜱ Bᴏᴛ Iꜱ Dᴏᴇꜱɴ'ᴛ Sᴜᴩᴩᴏʀᴛ Uᴩʟᴏᴀᴅɪɴɢ Fɪʟᴇꜱ Bɪɢɢᴇʀ Tʜᴀɴ 2Gʙ")

    try:
        await message.reply_text(
            text=f"**__Pʟᴇᴀꜱᴇ Eɴᴛᴇʀ Nᴇᴡ Fɪʟᴇɴᴀᴍᴇ...__**\n\n**Oʟᴅ Fɪʟᴇ Nᴀᴍᴇ** :- `{filename}`",
	    reply_to_message_id=message.id,  
	    reply_markup=ForceReply(True)
        )       
        await sleep(30)
    except FloodWait as e:
        await sleep(e.value)
        await message.reply_text(
            text=f"**__Pʟᴇᴀꜱᴇ Eɴᴛᴇʀ Nᴇᴡ Fɪʟᴇɴᴀᴍᴇ...__**\n\n**Oʟᴅ Fɪʟᴇ Nᴀᴍᴇ** :- `{filename}`",
	    reply_to_message_id=message.id,  
	    reply_markup=ForceReply(True)
        )
    except:
        pass
      
	
