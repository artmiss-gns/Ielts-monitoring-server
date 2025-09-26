# 🚀 Koyeb Deployment Guide

This guide covers deploying the IELTS Monitoring System to Koyeb, a serverless container platform.

## 📋 Prerequisites

- [Koyeb Account](https://app.koyeb.com/auth/signup)
- Docker image pushed to a registry (Docker Hub, GitHub Container Registry, etc.)
- Telegram Bot Token (optional, for notifications)

## 🏗️ Deployment Options

### Option 1: Deploy from Docker Hub (Recommended)

1. **Build and Push Image**:
   ```bash
   # Build the image
   docker build -t your-username/ielts-monitor:latest .
   
   # Push to Docker Hub
   docker push your-username/ielts-monitor:latest
   ```

2. **Deploy on Koyeb**:
   - Go to [Koyeb Dashboard](https://app.koyeb.com/)
   - Click "Create App"
   - Choose "Docker" as source
   - Enter image: `your-username/ielts-monitor:latest`

### Option 2: Deploy from GitHub (Auto-deploy)

1. **Push code to GitHub repository**
2. **Connect GitHub to Koyeb**:
   - In Koyeb Dashboard, choose "GitHub" as source
   - Select your repository
   - Koyeb will automatically detect the Dockerfile

## ⚙️ Koyeb Configuration

### Environment Variables

Set these in Koyeb's environment variables section:

```bash
# Required
PYTHONPATH=/app
TZ=Asia/Tehran

# Optional - Telegram Notifications
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Service Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| **Port** | `8080` | Health check port |
| **Health Check** | `/health` | Health endpoint (if implemented) |
| **CPU** | `0.1-0.5` | Adjust based on needs |
| **Memory** | `256MB-512MB` | Recommended for Python app |
| **Scaling** | `1 instance` | Single instance for monitoring |

### Command Override

In Koyeb's "Advanced" settings, set the command:

```bash
# For production monitoring (5-minute intervals)
python -m src.ielts_monitor --verbose --check-frequency 300

# For more frequent monitoring (1-minute intervals)
python -m src.ielts_monitor --verbose --check-frequency 60
```

## 🔧 Persistent Storage

**Important**: Koyeb is serverless and doesn't provide persistent storage. The notification state will reset on each deployment.

### Solutions:

1. **External Database** (Recommended):
   - Use PostgreSQL, MongoDB, or Redis
   - Store notification state externally
   
2. **Cloud Storage**:
   - AWS S3, Google Cloud Storage
   - Save/load notification state from cloud

3. **Accept State Reset**:
   - Simple approach for basic monitoring
   - State resets on each deployment

## 🚀 Deployment Steps

### 1. Prepare Your Image

```bash
# Clone repository
git clone your-repo-url
cd ielts-monitoring2

# Build optimized image for Koyeb
docker build --target production -t ielts-monitor:koyeb .

# Tag for registry
docker tag ielts-monitor:koyeb your-username/ielts-monitor:latest

# Push to registry
docker push your-username/ielts-monitor:latest
```

### 2. Create Koyeb App

1. **Login to Koyeb**: https://app.koyeb.com/
2. **Create New App**: Click "Create App"
3. **Configure Service**:
   ```
   Name: ielts-monitor
   Docker Image: your-username/ielts-monitor:latest
   Port: 8080
   Health Check: /
   ```

### 3. Set Environment Variables

```bash
PYTHONPATH=/app
TZ=Asia/Tehran
LOG_LEVEL=INFO
TELEGRAM_BOT_TOKEN=your_token  # Optional
TELEGRAM_CHAT_ID=your_chat_id  # Optional
```

### 4. Configure Command

```bash
python -m src.ielts_monitor --verbose --check-frequency 300
```

### 5. Deploy

Click "Deploy" and wait for deployment to complete.

## 📊 Monitoring & Logs

### View Logs
- Go to your app in Koyeb Dashboard
- Click on "Logs" tab
- View real-time application logs

### Health Monitoring
- Koyeb automatically monitors your app
- Restarts if health checks fail
- View metrics in the dashboard

### Scaling
- Koyeb auto-scales based on demand
- For IELTS monitoring, keep at 1 instance
- Scale up if needed for high-frequency monitoring

## 🔧 Configuration Examples

### Basic Monitoring (Recommended)
```bash
# Command
python -m src.ielts_monitor --verbose --check-frequency 300

# Environment
LOG_LEVEL=INFO
TZ=Asia/Tehran
```

### High-Frequency Monitoring
```bash
# Command  
python -m src.ielts_monitor --verbose --check-frequency 60

# Environment
LOG_LEVEL=DEBUG
TZ=Asia/Tehran
```

### With Notifications
```bash
# Command
python -m src.ielts_monitor --verbose --check-frequency 300

# Environment
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
LOG_LEVEL=INFO
TZ=Asia/Tehran
```

## 🛠️ Troubleshooting

### Common Issues

1. **App Crashes on Startup**:
   - Check logs in Koyeb dashboard
   - Verify environment variables
   - Ensure Dockerfile builds correctly

2. **No Notifications**:
   - Verify Telegram bot token and chat ID
   - Check logs for notification errors
   - Test bot token locally first

3. **High Memory Usage**:
   - Increase memory limit in Koyeb
   - Optimize check frequency
   - Monitor resource usage

### Debug Commands

```bash
# Test locally first
docker run --rm -e LOG_LEVEL=DEBUG ielts-monitor:koyeb --once --verbose

# Check health
curl -f https://your-app.koyeb.app/health
```

## 💰 Cost Optimization

### Koyeb Pricing Tips:
- **Free Tier**: 2 services, limited resources
- **Pay-as-you-go**: Based on actual usage
- **Optimize**: Use appropriate resource limits

### Resource Recommendations:
```
CPU: 0.1 vCPU (sufficient for monitoring)
Memory: 256MB (Python + dependencies)
Instances: 1 (no need for multiple)
```

## 🔄 Auto-Deployment

### GitHub Integration:
1. Connect your GitHub repository to Koyeb
2. Enable auto-deploy on push to main branch
3. Koyeb will rebuild and deploy automatically

### Webhook Deployment:
- Use Koyeb's webhook for manual deployments
- Trigger deployments from CI/CD pipelines

## 📚 Additional Resources

- [Koyeb Documentation](https://www.koyeb.com/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Telegram Bot Setup](https://core.telegram.org/bots#3-how-do-i-create-a-bot)

## 🆘 Support

For deployment issues:
1. Check Koyeb logs first
2. Verify Docker image works locally
3. Test environment variables
4. Contact Koyeb support if needed

---

**Note**: This deployment is optimized for Koyeb's serverless environment. The monitoring system will run continuously and restart automatically if it crashes.
