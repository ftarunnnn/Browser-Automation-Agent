FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies & Playwright requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirement files
COPY backend /app/backend
COPY pytest.ini /app/pytest.ini

# Install Python packages
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    pydantic-settings \
    sqlalchemy \
    aiosqlite \
    asyncpg \
    playwright \
    google-genai \
    openai \
    httpx \
    pytest \
    pytest-asyncio

# Install Playwright browser binaries
RUN python -m playwright install --with-deps chromium

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
