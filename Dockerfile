FROM python:3.12-slim

# Устанавливаем curl для healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app

RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости через uv
RUN uv pip install --system .

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]