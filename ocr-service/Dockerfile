FROM python:3.11-slim

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Python 依赖 (PaddleOCR + Web服务)
RUN pip install --no-cache-dir \
    paddlepaddle==3.0.0 \
    paddleocr>=2.9.0 \
    fastapi>=0.115 \
    uvicorn>=0.34 \
    python-multipart>=0.0.18 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制服务代码
COPY main.py .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
