FROM python:3.11-slim

WORKDIR /app

# System dependencies for OCR and native Python packages.
RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing \
    -o Acquire::Retries=3 \
    gcc \
    libffi-dev \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Runtime directories
RUN mkdir -p uploads exports

# 入口脚本：启动前对 MySQL 执行 Alembic 迁移，避免表缺失导致 lifespan 崩溃
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

ENTRYPOINT ["/entrypoint.sh"]
