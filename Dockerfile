# ====================================================================
# Finora: AI-Powered Personal Financial Manager & Investment Platform
# Production Multi-Stage Dockerfile
# ====================================================================

FROM python:3.12-slim AS runner

# Set environment variables for production execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    FLASK_ENV=production \
    FLASK_DEBUG=False

# Install system dependencies (curl for healthchecks, gcc/lib for database connectors)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root application user for cybersecurity compliance
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install Python package dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy application source code
COPY --chown=appuser:appuser . .

# Set permissions and switch to non-root user
USER appuser

# Expose HTTP port (configurable via PORT environment variable)
EXPOSE 5000

# Health check verifying the /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/health || exit 1

# Production Entrypoint: Run bootstrap pre-flight check, then start Gunicorn WSGI server
CMD ["sh", "-c", "python bootstrap.py && exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 4 --threads 2 --timeout 120 --access-logfile - --error-logfile - wsgi:app"]
