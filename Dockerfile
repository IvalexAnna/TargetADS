FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir -e .

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]