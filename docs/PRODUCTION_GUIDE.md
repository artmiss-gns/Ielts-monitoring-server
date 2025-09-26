# 🚀 IELTS Monitor - Production Deployment Guide

## 📋 Pre-Deployment Checklist

### 1. **Telegram Setup** ✅
```bash
# Create .env file with your credentials
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 2. **Configuration** ✅
```yaml
# config.yaml is already configured for production
base_url: 'https://irsafam.org'
check_frequency: 300  # 5 minutes
cities:
  - isfahan
  # Add more cities as needed
```

### 3. **Dependencies** ✅
```bash
uv sync  # All dependencies installed
```

## 🎯 Production Commands

### **Start Monitoring (Recommended)**
```bash
# Production monitoring with 5-minute intervals
uv run python -m src.ielts_monitor

# Custom frequency (e.g., 3 minutes = 180 seconds)
uv run python -m src.ielts_monitor --check-frequency 180

# Monitor multiple cities
uv run python -m src.ielts_monitor --cities tehran isfahan shiraz
```

### **Testing Commands**
```bash
# Test with single scan
uv run python -m src.ielts_monitor --once

# Test with verbose logging
uv run python -m src.ielts_monitor --once --verbose

# Clear notification state if needed
uv run python -m src.ielts_monitor --clear-notifications
```

## 🔄 Background Deployment

### **Option 1: Using nohup**
```bash
nohup uv run python -m src.ielts_monitor > ielts_monitor.log 2>&1 &
```

### **Option 2: Using screen**
```bash
screen -S ielts-monitor
uv run python -m src.ielts_monitor
# Press Ctrl+A, then D to detach
```

### **Option 3: Using systemd (Linux)**
Create `/etc/systemd/system/ielts-monitor.service`:
```ini
[Unit]
Description=IELTS Appointment Monitor
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/ielts-monitoring2
ExecStart=/usr/local/bin/uv run python -m src.ielts_monitor
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable ielts-monitor
sudo systemctl start ielts-monitor
sudo systemctl status ielts-monitor
```

## 📊 Monitoring & Logs

### **View Logs**
```bash
# Real-time log viewing
tail -f logs/ielts_monitor.log

# Check recent activity
tail -100 logs/ielts_monitor.log
```

### **Expected Output**
```
🚀 Starting IELTS appointment monitoring
🏙️  Monitoring cities: isfahan
📚 Monitoring exam models: cdielts
📅 Monitoring months: 10
🔔 Notifications enabled: ✅
⏱️  Check frequency: 300 seconds

🔄 [17:05:39] SCANNING - Checking IELTS appointment availability...
============================================================
😔 NO AVAILABLE SLOTS: All appointments are currently filled
============================================================
🔄 [17:10:39] WAITING - Next scan in 300 seconds
```

### **When New Slots Are Found**
```
🆕 NEW SLOT ALERT: 1 new appointment just became available!
🎯 Slot 1 Found:
   📅 Date: 2025-10-29
   🕐 Time: صبح (۰۸:۳۰ - ۱۱:۳۰)
   📍 Location: اصفهان (ایده نواندیش)
📤 NOTIFICATION SENT: Alert delivered for 2025-10-29 at اصفهان (ایده نواندیش)
```

## 🚨 Troubleshooting

### **Common Issues**

1. **No notifications received**
   ```bash
   # Check Telegram credentials
   echo $TELEGRAM_BOT_TOKEN
   echo $TELEGRAM_CHAT_ID
   
   # Test with single scan
   uv run python -m src.ielts_monitor --once --verbose
   ```

2. **Connection errors**
   ```bash
   # Check internet connection
   curl -I https://irsafam.org
   
   # Test with verbose logging
   uv run python -m src.ielts_monitor --once --verbose
   ```

3. **Clear notification state**
   ```bash
   # If you want to re-notify about existing slots
   uv run python -m src.ielts_monitor --clear-notifications
   ```

## 🎉 Success Indicators

### **System is Working When You See:**
- ✅ Regular scanning messages every 5 minutes
- ✅ "SCANNING - Checking IELTS appointment availability..."
- ✅ "NO AVAILABLE SLOTS" or "SLOTS FOUND" messages
- ✅ "WAITING - Next scan in 300 seconds"

### **New Slot Detection Working When You See:**
- ✅ "NEW SLOT ALERT: X new appointments just became available!"
- ✅ "NOTIFICATION SENT: Alert delivered for..."
- ✅ Telegram message received in your channel

## 📱 Expected Telegram Notifications

```
🎯 New IELTS Slot Available!

📅 Date: 2025-10-29
🕐 Time: صبح (۰۸:۳۰ - ۱۱:۳۰)
📍 Location: اصفهان (ایده نواندیش)
📝 Exam Type: cdielts - (Ac/Gt)
💰 Price: ۲۹۱,۱۱۵,۰۰۰ ریال
🔗 URL: https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=cdielts&month%5B%5D=10

Don't miss this opportunity!
```

## 🎯 **READY FOR PRODUCTION!** ✅

Your IELTS monitoring system is now fully configured and ready to monitor the real website. Simply run:

```bash
uv run python -m src.ielts_monitor
```

And you'll receive instant notifications when new IELTS appointments become available! 🎊
