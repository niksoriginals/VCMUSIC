import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import AudioPiped
import yt_dlp

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("musicbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
pytg = PyTgCalls(app)


# === YouTube Downloader (audio only) ===
def yt_search(query: str):
    opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "extract_flat": False,
        "outtmpl": "downloads/%(title)s.%(ext)s",
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)["entries"][0]
        return info["title"], ydl.prepare_filename(info)


# === Start Command ===
@app.on_message(filters.command("start"))
async def start(_, m):
    await m.reply("🎶 Music Bot Online! Use /play <song name>")


# === Play Command ===
@app.on_message(filters.command("play"))
async def play(_, m):
    if len(m.command) < 2:
        return await m.reply("⚠️ Please give a song name!")

    query = " ".join(m.command[1:])
    await m.reply(f"🔎 Searching `{query}`...")

    title, file = yt_search(query)

    chat_id = m.chat.id
    await pytg.join_group_call(chat_id, AudioPiped(file))

    await m.reply(f"▶️ Now Playing: **{title}**")


# === Stop Command ===
@app.on_message(filters.command("stop"))
async def stop(_, m):
    chat_id = m.chat.id
    await pytg.leave_group_call(chat_id)
    await m.reply("⏹️ Music Stopped!")


# === Run ===
pytg.start()
app.start()
print("🚀 Music Bot Started!")
idle()
