# Dockerfile for IELTS simulation server
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN groupadd -r simulation && \
    useradd -r -g simulation -d /app simulation && \
    chown -R simulation:simulation /app

# Copy application files
COPY --chown=simulation:simulation . .

# Create necessary directories
RUN mkdir -p /app/data /app/static && \
    chown -R simulation:simulation /app

# Switch to non-root user
USER simulation

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the simulation server
CMD ["python", "server.py"]
