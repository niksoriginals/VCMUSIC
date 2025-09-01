# musicbot.py
import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import InputStream, InputAudioStream
import yt_dlp

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")
OWNER_ID = int(os.getenv("OWNER_ID"))

app = Client(STRING_SESSION, api_id=API_ID, api_hash=API_HASH)
pytg = PyTgCalls(app)

queues = {}

ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "quiet": True,
    "noplaylist": True,
}

os.makedirs("downloads", exist_ok=True)

def download_audio(url: str):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info:
            return ydl.prepare_filename(info)
    return None

@app.on_message(filters.command("join") & filters.user(OWNER_ID))
async def join(_, msg):
    chat_id = msg.chat.id
    await pytg.join_group_call(
        chat_id,
        InputAudioStream("downloads/silence.raw")
    )
    await msg.reply_text("✅ Joined VC")

@app.on_message(filters.command("play") & filters.user(OWNER_ID))
async def play(_, msg):
    chat_id = msg.chat.id
    if len(msg.command) < 2:
        return await msg.reply_text("Usage: /play <YouTube link>")
    url = msg.command[1]
    await msg.reply_text("⬇️ Downloading...")
    file = download_audio(url)
    if not file:
        return await msg.reply_text("❌ Download failed")
    raw = file.rsplit(".", 1)[0] + ".raw"
    os.system(f'ffmpeg -y -i "{file}" -f s16le -ac 2 -ar 48000 "{raw}"')
    queues.setdefault(chat_id, []).append(raw)
    await msg.reply_text("▶️ Added to queue")
    if len(queues[chat_id]) == 1:
        await _play_next(chat_id)

async def _play_next(chat_id):
    while queues.get(chat_id):
        raw = queues[chat_id][0]
        await pytg.change_stream(chat_id, InputStream(InputAudioStream(raw)))
        await asyncio.sleep(30)  # simple wait (replace with exact duration)
        queues[chat_id].pop(0)

@app.on_message(filters.command("stop") & filters.user(OWNER_ID))
async def stop(_, msg):
    chat_id = msg.chat.id
    queues[chat_id] = []
    await msg.reply_text("⏹️ Stopped")

async def main():
    await app.start()
    await pytg.start()
    print("🎶 Bot started")
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
