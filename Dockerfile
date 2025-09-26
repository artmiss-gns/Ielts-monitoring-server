# Multi-stage build for production-ready IELTS monitoring system
FROM python:3.11-slim AS builder

# Set build environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Configure apt for better reliability
RUN echo 'Acquire::Retries "3";' > /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::http::Timeout "60";' >> /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::ftp::Timeout "60";' >> /etc/apt/apt.conf.d/80-retries

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv for fast dependency management with retry logic
RUN pip install --no-cache-dir --retries 3 --timeout 60 uv

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim AS production

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    TZ=UTC

# Configure apt for better reliability
RUN echo 'Acquire::Retries "3";' > /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::http::Timeout "60";' >> /etc/apt/apt.conf.d/80-retries

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    tzdata \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create application user and directories
RUN groupadd -r ielts && \
    useradd -r -g ielts -d /app -s /bin/bash ielts && \
    mkdir -p /app/data /app/logs /app/config && \
    chown -R ielts:ielts /app

# Set working directory
WORKDIR /app

# Copy application source code
COPY --chown=ielts:ielts src/ ./src/
COPY --chown=ielts:ielts config.yaml ./config/config.yaml

# Create volume mount points
VOLUME ["/app/data", "/app/logs", "/app/config"]

# Switch to non-root user
USER ielts

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys, os; sys.exit(0 if os.path.exists('/app/src/ielts_monitor/__main__.py') else 1)" || exit 1

# Expose port for potential web interface (future enhancement)
EXPOSE 8080

# Set entrypoint and default command
ENTRYPOINT ["python", "-m", "src.ielts_monitor"]
CMD ["--verbose"]