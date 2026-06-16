FROM python:3.11-slim

WORKDIR /app

# 系统依赖 (libgl1-mesa-glx 在 Debian trixie 中已改为 libgl1)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libgl1 \
    libglib2.0-0 \
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

# 启动
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
