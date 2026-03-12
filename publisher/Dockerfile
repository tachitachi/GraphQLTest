FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir redis

COPY publisher.py /app/publisher.py

CMD ["python", "/app/publisher.py"]

