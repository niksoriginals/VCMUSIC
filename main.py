import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import AudioPiped
import yt_dlp

# === CONFIG ===
API_ID = int("YOUR_API_ID")  # apna api id daal
API_HASH = "YOUR_API_HASH"   # apna api hash daal
BOT_TOKEN = "YOUR_BOT_TOKEN" # apna bot token daal

# Pyrogram client
app = Client(
    "music-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# PyTgCalls client
call_py = PyTgCalls(app)

# === DOWNLOAD YT AUDIO ===
def download_audio(url: str) -> str:
    opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# === HANDLER: /play [url or query] ===
@app.on_message(filters.command("play") & filters.group)
async def play(_, message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: /play [YouTube URL or query]")

    query = " ".join(message.command[1:])

    # Check if it's a URL or a search query
    if query.startswith("http://") or query.startswith("https://"):
        url = query
    else:
        # Search on YT
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
            url = info["webpage_url"]

    await message.reply_text(f"⏳ Downloading audio from: {url}")
    audio_path = download_audio(url)

    chat_id = message.chat.id
    try:
        await call_py.join_group_call(
            chat_id,
            AudioPiped(audio_path),
        )
        await message.reply_text("🎶 Now playing audio in VC!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# === START ===
async def main():
    await app.start()
    await call_py.start()
    print("✅ Bot is running...")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
