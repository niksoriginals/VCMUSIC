# --- Base image ---
FROM python:3.11-slim

# --- System dependencies (for pytgcalls / ffmpeg etc) ---
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    libavformat-dev \
    libavdevice-dev \
    libavutil-dev \
    libswresample-dev \
    libswscale-dev \
    && rm -rf /var/lib/apt/lists/*

# --- Workdir ---
WORKDIR /app

# --- Copy files ---
COPY . .

# --- Install python deps ---
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- Run bot ---
CMD ["python", "main.py"]
