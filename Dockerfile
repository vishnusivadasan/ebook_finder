# Ultra-minimal FastAPI build with Debian Slim
FROM python:3.12-slim

# Install minimal system dependencies with GPG key handling for ARM/Pi compatibility
RUN apt-get update --allow-insecure-repositories && \
    apt-get install -y --no-install-recommends --allow-unauthenticated \
    curl \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements.txt

# Install Python dependencies using pre-built wheels
RUN pip install --no-cache-dir --no-compile --disable-pip-version-check \
    -r requirements.txt \
    && find /usr/local/lib/python3.12 -name "*.pyc" -delete \
    && find /usr/local/lib/python3.12 -name "__pycache__" -type d -exec rm -rf {} + \
    && rm -rf /root/.cache/pip

# Copy application files
COPY app.py app.py
COPY ebook_search.py .
COPY templates/ templates/
COPY static/ static/

# Create mount points, static directory, and cache directory
RUN mkdir -p /mnt/{ebooks,documents,downloads,books,desktop,calibre} \
    && mkdir -p /tmp/app-cache

# Create non-root user
RUN groupadd -g 1000 app && useradd -u 1000 -g app -s /bin/sh -m app

# Change ownership
RUN chown -R app:app /app /tmp/app-cache

# Switch to non-root user
USER app

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

# Expose port
EXPOSE 8501

# Run FastAPI with uvicorn - use loop configuration for ARM/Pi compatibility
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8501", "--loop", "asyncio", "--no-use-colors"] 
