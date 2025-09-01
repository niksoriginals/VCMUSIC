# musicbot.py
import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import StreamType
from pytgcalls.types.input_stream import AudioPiped
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

# --- Audio Downloader ---
def download_audio(query: str):
    opts = ydl_opts.copy()
    opts.update({
        "default_search": "ytsearch1",  # search YouTube
    })
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if "entries" in info:  # search result
            info = info["entries"][0]
        return ydl.prepare_filename(info), info.get("title", "Unknown Title")
    return None, None

# --- VC Join Command ---
@app.on_message(filters.command("join") & filters.user(OWNER_ID))
async def join(_, msg):
    chat_id = msg.chat.id
    silence = "downloads/silence.mp3"
    if not os.path.exists(silence):
        os.system(
            f'ffmpeg -f lavfi -i anullsrc=r=48000:cl=stereo -t 5 "{silence}" -y'
        )

    await pytg.join_group_call(
        chat_id,
        AudioPiped(silence),
        stream_type=StreamType().local_stream
    )
    await msg.reply_text("✅ Joined VC")

# --- Play Command ---
@app.on_message(filters.command("play") & filters.user(OWNER_ID))
async def play(_, msg):
    chat_id = msg.chat.id
    if len(msg.command) < 2:
        return await msg.reply_text("Usage: /play <song name>")

    query = " ".join(msg.command[1:])
    await msg.reply_text(f"🔍 Searching: {query}")
    file, title = download_audio(query)
    if not file:
        return await msg.reply_text("❌ Download failed")

    raw = file.rsplit(".", 1)[0] + ".raw"
    os.system(f'ffmpeg -y -i "{file}" -f s16le -ac 2 -ar 48000 "{raw}"')

    queues.setdefault(chat_id, []).append(raw)
    await msg.reply_text(f"▶️ Added to queue: {title}")

    if len(queues[chat_id]) == 1:
        await _play_next(chat_id)

# --- Queue Player ---
async def _play_next(chat_id):
    while queues.get(chat_id):
        raw = queues[chat_id][0]
        await pytg.change_stream(
            chat_id,
            AudioPiped(raw),
            stream_type=StreamType().local_stream
        )
        await asyncio.sleep(30)  # TODO: replace with song duration
        queues[chat_id].pop(0)

# --- Stop Command ---
@app.on_message(filters.command("stop") & filters.user(OWNER_ID))
async def stop(_, msg):
    chat_id = msg.chat.id
    queues[chat_id] = []
    await msg.reply_text("⏹️ Stopped")

# --- Main ---
async def main():
    await app.start()
    await pytg.start()
    print("🎶 Bot started")
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
