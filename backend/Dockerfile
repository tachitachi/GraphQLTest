FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install Python dependencies with Poetry (no virtualenv inside container)
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi --only main

COPY . .

# Install the project itself (executes the 'packages' mapping in pyproject.toml)
RUN poetry install --no-interaction --no-ansi --only main

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

