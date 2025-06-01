# Ultra-minimal FastAPI build
FROM python:3.12-alpine

# Install build dependencies and remove after
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    && apk add --no-cache libstdc++ \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt requirements.txt

# Install Python dependencies with minimal footprint
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

# Create mount directories and app directories
RUN mkdir -p /mnt/{ebooks,documents,downloads,books,desktop,calibre} \
    && mkdir -p /app/static \
    && mkdir -p /tmp/app-cache

# Create non-root user
RUN addgroup -g 1000 -S app && adduser -u 1000 -S app -G app

# Change ownership of app directory to app user
RUN chown -R app:app /app /tmp/app-cache

# Change to non-root user
USER app

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8501

# Run FastAPI with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8501"] 