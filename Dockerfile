FROM python:3.11-slim-bookworm

# libgpiod2: runtime dep for adafruit-blinka GPIO on Debian
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgpiod2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary -r requirements.txt

COPY . .

CMD ["python", "main.py"]
