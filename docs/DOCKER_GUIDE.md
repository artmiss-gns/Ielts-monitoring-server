# 🐳 Docker Deployment Guide

This guide covers the complete Docker deployment setup for the IELTS Monitoring System.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Docker Architecture](#docker-architecture)
- [Configuration](#configuration)
- [Deployment Options](#deployment-options)
- [Monitoring & Logs](#monitoring--logs)
- [Troubleshooting](#troubleshooting)
- [Security](#security)

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 512MB RAM minimum
- 1GB disk space

### Basic Deployment

```bash
# Clone and navigate to project
git clone <repository-url>
cd Ielts-monitoring2

# Start with default configuration
docker-compose up -d

# View logs
docker-compose logs -f ielts-monitor
```

## 🏗️ Docker Architecture

### Multi-Stage Build

The Dockerfile uses a multi-stage build approach:

1. **Builder Stage**: Installs dependencies and builds the application
2. **Production Stage**: Creates minimal runtime image with security hardening

### Key Features

- ✅ **Security**: Non-root user, read-only filesystem, no-new-privileges
- ✅ **Performance**: Multi-stage build, optimized layers, minimal base image
- ✅ **Monitoring**: Health checks, resource limits, logging configuration
- ✅ **Persistence**: Named volumes for data and logs
- ✅ **Networking**: Isolated network with proper service discovery

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TZ` | `Asia/Tehran` | Timezone for the container |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `PYTHONPATH` | `/app` | Python module path |
| `ENVIRONMENT` | `production` | Runtime environment |

### Volume Mounts

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./config.yaml` | `/app/config/config.yaml` | Main configuration file |
| `ielts_data` | `/app/data` | Persistent data (notification state) |
| `ielts_logs` | `/app/logs` | Application logs |

### Configuration File

Create or modify `config.yaml`:

```yaml
# IELTS Monitoring Configuration
base_url: 'https://irsafam.org/ielts/timetable'
cities:
  - isfahan
exam_models:
  - cdielts
months:
  - 10
  - 11
check_frequency: 300  # 5 minutes for production
show_unavailable: false
no_ssl_verify: false
```

## 🚀 Deployment Options

### 1. Development Mode

```bash
# Use development override
docker-compose up -d

# Or explicitly use dev profile
docker-compose --profile dev up -d ielts-monitor-dev
```

**Features:**
- Source code mounting for live development
- Debug logging enabled
- Faster check intervals
- No resource limits

### 2. Production Mode

```bash
# Use production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Features:**
- Resource limits and security hardening
- Automatic restarts and health monitoring
- Optimized logging configuration
- Watchtower for automatic updates

### 3. Testing with Simulation

```bash
# Start with simulation server
docker-compose --profile simulation up -d

# Update config to use simulation server
# base_url: 'http://ielts-simulation:8000'
```

### 4. Full Monitoring Stack

```bash
# Start with monitoring services
docker-compose --profile monitoring up -d
```

**Includes:**
- Log viewer on port 8080
- Watchtower for container updates
- Health monitoring

## 📊 Monitoring & Logs

### Viewing Logs

```bash
# Real-time logs
docker-compose logs -f ielts-monitor

# Last 100 lines
docker-compose logs --tail=100 ielts-monitor

# Logs from specific time
docker-compose logs --since="2024-01-01T00:00:00Z" ielts-monitor
```

### Health Checks

```bash
# Check container health
docker-compose ps

# Detailed health status
docker inspect ielts-monitor-app --format='{{.State.Health.Status}}'
```

### Resource Monitoring

```bash
# Container resource usage
docker stats ielts-monitor-app

# System resource usage
docker system df
```

### Log Viewer (Optional)

Access the web-based log viewer at `http://localhost:8080` when using the monitoring profile.

## 🔧 Management Commands

### Building Images

```bash
# Build with helper script
./docker/docker-build.sh --type production --latest

# Manual build
docker build -t ielts-monitor:latest .
```

### Data Management

```bash
# Backup data volume
docker run --rm -v ielts-monitor-data:/data -v $(pwd):/backup alpine tar czf /backup/ielts-data-backup.tar.gz -C /data .

# Restore data volume
docker run --rm -v ielts-monitor-data:/data -v $(pwd):/backup alpine tar xzf /backup/ielts-data-backup.tar.gz -C /data

# Clear notification state
docker-compose exec ielts-monitor rm -f /app/data/notification_state.json
```

### Container Management

```bash
# Restart service
docker-compose restart ielts-monitor

# Update and restart
docker-compose pull && docker-compose up -d

# Scale service (if needed)
docker-compose up -d --scale ielts-monitor=2
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Permission Denied

```bash
# Fix volume permissions
sudo chown -R 1000:1000 ./data ./logs
```

#### 2. Configuration Not Loading

```bash
# Check config file syntax
docker-compose exec ielts-monitor python -c "import yaml; yaml.safe_load(open('/app/config/config.yaml'))"

# Verify mount
docker-compose exec ielts-monitor ls -la /app/config/
```

#### 3. Network Connectivity Issues

```bash
# Test network from container
docker-compose exec ielts-monitor curl -I https://irsafam.org

# Check DNS resolution
docker-compose exec ielts-monitor nslookup irsafam.org
```

#### 4. Memory Issues

```bash
# Check memory usage
docker stats ielts-monitor-app

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 512M
```

### Debug Mode

```bash
# Run in debug mode
docker-compose exec ielts-monitor python -m src.ielts_monitor --verbose --once

# Interactive shell
docker-compose exec ielts-monitor /bin/bash
```

### Log Analysis

```bash
# Search for errors
docker-compose logs ielts-monitor 2>&1 | grep -i error

# Monitor notification events
docker-compose logs -f ielts-monitor | grep "NOTIFICATION"

# Check startup sequence
docker-compose logs ielts-monitor | head -50
```

## 🔒 Security

### Security Features

- **Non-root execution**: Application runs as `ielts` user (UID 1000)
- **Read-only filesystem**: Container filesystem is read-only except for specific paths
- **No new privileges**: Prevents privilege escalation
- **Resource limits**: CPU and memory limits prevent resource exhaustion
- **Network isolation**: Services run in isolated Docker network
- **Minimal attack surface**: Slim base image with minimal packages

### Security Best Practices

1. **Keep images updated**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

2. **Regular security scans**:
   ```bash
   docker scout cves ielts-monitor:latest
   ```

3. **Monitor logs for suspicious activity**:
   ```bash
   docker-compose logs ielts-monitor | grep -E "(error|fail|unauthorized)"
   ```

4. **Use secrets for sensitive data**:
   ```bash
   # Use Docker secrets or environment files
   echo "TELEGRAM_TOKEN=your_token" > .env
   ```

### Hardening Checklist

- [ ] Use specific image tags, not `latest`
- [ ] Regularly update base images
- [ ] Scan images for vulnerabilities
- [ ] Use read-only filesystems where possible
- [ ] Implement proper logging and monitoring
- [ ] Use secrets management for sensitive data
- [ ] Regular backup of persistent data

## 📚 Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Container Security](https://docs.docker.com/engine/security/)

## 🆘 Support

For issues and questions:

1. Check the [troubleshooting section](#troubleshooting)
2. Review container logs: `docker-compose logs ielts-monitor`
3. Verify configuration: `docker-compose config`
4. Test connectivity: `docker-compose exec ielts-monitor curl -I https://irsafam.org`

---

**Note**: This Docker setup is production-ready and includes comprehensive security, monitoring, and management features for reliable IELTS appointment monitoring.
