FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Install system dependencies if needed (e.g., redis-cli)
RUN apt-get update && apt-get install -y redis-tools && rm -rf /var/lib/apt/lists/*

EXPOSE 80

CMD ["python", "src/bot.py"]
