# Ultra-minimal FastAPI build
FROM python:3.12-alpine

# Install system dependencies including C++ compiler for python-Levenshtein
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    g++ \
    musl-dev \
    make \
    cmake

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --no-compile --disable-pip-version-check \
    -r requirements.txt \
    && apk del .build-deps \
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
RUN addgroup -g 1000 -S app && adduser -u 1000 -S app -G app

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

# Run FastAPI with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8501"] 