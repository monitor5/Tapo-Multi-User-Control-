# =============================================================================
# UNIFIED DOCKERFILE
# =============================================================================
# Multi-stage build supporting both development and production

FROM python:3.12-slim

LABEL authors="uhyun"
LABEL description="Tapo Control - Smart Plug Management System"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies including gosu for user switching
RUN apt-get update && apt-get install -y \
    curl \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user first
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create startup script to handle permissions
RUN echo '#!/bin/bash\n\
# Fix database file permissions if it exists\n\
if [ -f /app/users.db ]; then\n\
    chown appuser:appuser /app/users.db\n\
    chmod 664 /app/users.db\n\
fi\n\
\n\
# Create data directory if it does not exist\n\
mkdir -p /app/data\n\
chown appuser:appuser /app/data\n\
\n\
# Switch to appuser and start the application\n\
exec gosu appuser uvicorn app.main:app --host 0.0.0.0 --port 5011\n\
' > /app/start.sh && chmod +x /app/start.sh

# Set ownership of app directory
RUN chown -R appuser:appuser /app

# Expose port
EXPOSE 5011

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5011/healthz || exit 1

# Start application with permission fixing script
CMD ["/app/start.sh"]
