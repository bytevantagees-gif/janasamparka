FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies with caching enabled
# Using buildkit cache mount to speed up rebuilds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create backups directory
RUN mkdir -p /app/backups && chmod 777 /app/backups

# Expose port
EXPOSE 8000

# Use shell form to run both init and server
CMD bash /app/init-db.sh && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
