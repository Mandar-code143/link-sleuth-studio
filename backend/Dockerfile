FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for compiling lxml if wheels not available
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 4000

ENV APP_ENV=production
ENV APP_PORT=4000

# Respect dynamic $PORT if provided by hosting environments (Cloud Run, Render, Railway, Fly.io)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-${APP_PORT:-4000}}"]
