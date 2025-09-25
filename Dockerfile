# Use a minimal Python image as the base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Copy the standalone script and sample HTML file
COPY run.py ./
COPY sample-html-page.html ./

# Install required dependencies
RUN uv pip install --no-cache-dir requests beautifulsoup4

# Create a non-root user to run the application
RUN groupadd -r ielts && \
    useradd -r -g ielts ielts && \
    chown -R ielts:ielts /app

# Switch to non-root user
USER ielts

# Make the script executable
RUN chmod +x run.py

# Set entrypoint
ENTRYPOINT ["python", "run.py"]

# Default command (can be overridden)
CMD ["--once", "--use-sample"]