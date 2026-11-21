FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
# CPU-only PyTorch first: the default Linux wheels add several GB of CUDA libraries this image cannot use.
# Versions must match requirements.txt.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.15.0 torchvision==0.29.2 \
    && pip install --no-cache-dir -r requirements.txt
COPY . .
