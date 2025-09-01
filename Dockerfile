FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir pyrogram tgcrypto pytgcalls yt-dlp
CMD ["python", "musicbot.py"]
