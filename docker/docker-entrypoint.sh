#!/bin/bash
set -e

# Docker entrypoint script for IELTS monitoring system
# This script handles initialization and configuration

echo "🚀 Starting IELTS Monitoring System..."

# Create necessary directories
mkdir -p /app/data /app/logs /app/config

# Set proper permissions
chown -R ielts:ielts /app/data /app/logs

# Check if config file exists
if [ ! -f "/app/config/config.yaml" ]; then
    echo "⚠️  No config file found, using default configuration"
    cp /app/config/config.yaml.default /app/config/config.yaml 2>/dev/null || true
fi

# Validate configuration
echo "🔍 Validating configuration..."
python -c "
import yaml
import sys
try:
    with open('/app/config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print('✅ Configuration is valid')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    sys.exit(1)
"

# Check network connectivity
echo "🌐 Checking network connectivity..."
python -c "
import requests
import sys
try:
    response = requests.get('https://httpbin.org/status/200', timeout=10)
    print('✅ Network connectivity OK')
except Exception as e:
    print(f'⚠️  Network check failed: {e}')
"

# Initialize notification state if it doesn't exist
if [ ! -f "/app/data/notification_state.json" ]; then
    echo "📝 Initializing notification state..."
    echo '{}' > /app/data/notification_state.json
fi

echo "✅ Initialization complete!"
echo "🎯 Starting monitoring with arguments: $@"

# Execute the main command
exec "$@"
