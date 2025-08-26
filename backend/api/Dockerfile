# syntax=docker/dockerfile:1
FROM python:3.10-slim AS api

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos requirements del backend
COPY requirements.txt .

RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo el backend, incluida la carpeta api/
COPY . .

EXPOSE 8001

CMD ["/app/venv/bin/uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]
