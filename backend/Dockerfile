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

EXPOSE 8080

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
