FROM python:3.11-slim as builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/bin/ffmpeg /usr/bin/
WORKDIR /app
COPY . .

ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
