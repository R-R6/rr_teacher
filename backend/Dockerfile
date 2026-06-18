FROM python:3.11-slim

WORKDIR /app

# 系统依赖 (libgl1-mesa-glx 在 Debian trixie 中已改为 libgl1)
# Tesseract-OCR + 中文简体语言包
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

# Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制源码
COPY . .

# 创建必要目录
RUN mkdir -p uploads exports

# 云托管端口 8080
EXPOSE 8080

# Tesseract 环境变量
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

# 启动
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
