# Multi-Stage Production Dockerfile for ULTRON Backend Engine
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final Production Stage
FROM python:3.11-slim as runner

WORKDIR /app

# Install Playwright Chromium & System Dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python dependencies
COPY --from=builder /install /usr/local

# Install Playwright browser binaries
RUN python -m playwright install chromium --with-deps || true

# Security: Create non-root user and group
RUN groupadd -g 10001 ultron && \
    useradd -u 10000 -g ultron -s /bin/bash -m ultron && \
    mkdir -p /app/backend/app/database /app/sandbox /app/logs && \
    chown -R ultron:ultron /app

COPY --chown=ultron:ultron backend /app/backend
COPY --chown=ultron:ultron database /app/database

USER ultron

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
