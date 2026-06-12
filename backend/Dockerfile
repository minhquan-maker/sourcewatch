FROM python:3.11-slim

WORKDIR /app

# Install system deps for Playwright + lxml
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first, install Python deps (includes playwright==1.49.1)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now install Chromium using the SAME playwright version from requirements.txt
# This ensures binary version matches Python package version
RUN playwright install chromium

# Copy app
COPY . .

# Create data directories (app-internal, not persistent disk)
RUN mkdir -p /app/data/chromadb

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]