#
# Build from repository root (admin console must be built first):
#   node admin-web/scripts/build.mjs
#   docker build -f backend/Dockerfile -t ccr.ccs.tencentyun.com/chem-teacher/backend:v29 .
#
# admin-dist is copied to /frontend/admin-dist for app.main mount resolution.

FROM python:3.11-slim

WORKDIR /app

# System dependencies for OCR and native Python packages.
RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing \
    -o Acquire::Retries=3 \
    gcc \
    libffi-dev \
    libgl1 \
    libglib2.0-0 \
    tzdata \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-eng \
    && ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY frontend/admin-dist /frontend/admin-dist

RUN test -f /frontend/admin-dist/index.html

RUN mkdir -p uploads exports

COPY backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/
ENV TZ=Asia/Shanghai

ENTRYPOINT ["/entrypoint.sh"]
