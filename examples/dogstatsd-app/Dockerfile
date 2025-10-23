# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create non-root user for security
RUN groupadd -g 1001 appuser && \
    useradd -r -u 1001 -g appuser appuser

# Change ownership of the app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set default environment variables
ENV DOGSTATSD_HOST=localhost
ENV DOGSTATSD_PORT=8125
ENV OTLP_ENDPOINT=http://sumo-sumologic-metadata-metrics.default.svc.cluster.local.:4318/v1/metrics
ENV APP_NAME=dogstatsd-sample-app
ENV METRIC_INTERVAL=10

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(5); s.connect(('$DOGSTATSD_HOST', int('$DOGSTATSD_PORT'))); s.close()" || exit 1

# Expose port for potential HTTP health endpoint
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]