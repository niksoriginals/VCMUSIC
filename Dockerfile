FROM python:3.11-slim

# --- Install system deps ---
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# --- Set workdir ---
WORKDIR /app

# --- Copy files ---
COPY requirements.txt .

# --- Install python deps ---
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- Copy source code ---
COPY . .

# --- Run bot ---
CMD ["python", "main.py"]
