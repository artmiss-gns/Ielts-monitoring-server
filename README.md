# IELTS Monitoring

A professional, production-ready application that monitors the Irsafam website (https://irsafam.org/ielts/timetable) for available IELTS exam slots. This tool provides real-time monitoring with instant Telegram notifications when new appointments become available.

## ✨ Features

- **🚀 Production-Ready Monitoring**: Continuous real-time tracking with professional logging
- **📱 Instant Telegram Notifications**: Get immediate alerts when new slots become available
- **🎨 Enhanced Terminal UI**: Beautiful, colorful logging with emojis and professional formatting
- **🧠 Smart State Management**: Prevents duplicate notifications and handles slot re-availability
- **⚡ No Rate Limiting**: Optimized for IELTS monitoring - get notified about every available slot
- **🔄 HTTP Fallback**: Reliable notification delivery even when libraries have compatibility issues
- **📊 Real-time Status Updates**: Clear indicators for scanning, new slots, and notification delivery
- **🛡️ Robust Error Handling**: Graceful handling of network issues and API limits
- **⚙️ Flexible Configuration**: YAML configuration with command-line overrides
- **🐳 Containerized**: Docker support for easy deployment
- **📝 Comprehensive Logging**: File and console logging with different verbosity levels

## Installation

### Using Python

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd ielts-monitoring2
   ```

2. Install the required dependencies using [uv](https://github.com/astral-sh/uv) (recommended):
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

### Using Docker

Build the Docker image:
```bash
docker build -t ielts-monitor .
```

## Configuration

The application reads settings from a `config.yaml` file by default. You can customize this file to set your preferred monitoring parameters:

```yaml
# Configuration for IELTS appointment monitoring
cities:
  - isfahan

# Exam models to check (cdielts, pdielts)
exam_models:
  - cdielts

# Months to check (1-12, e.g., 10 for October, 11 for November)
months:
  - 10
  - 11

# Monitoring frequency in seconds
check_frequency: 3600

# Show unavailable/filled slots in output
show_unavailable: false

# Disable SSL certificate verification (use with caution)
no_ssl_verify: false
```

Any command-line arguments you provide will override the corresponding settings from the config file.

## Telegram Notifications Setup

To receive notifications when new IELTS slots become available:

1. **Create a Telegram Bot:**
   - Message @BotFather on Telegram
   - Send `/newbot` and follow the instructions
   - Save the bot token you receive

2. **Create a Channel:**
   - Create a new channel or use an existing one
   - Add your bot as an administrator to the channel
   - Get the channel's chat ID (you can use @userinfobot for this)

3. **Set Environment Variables:**
   Create a `.env` file in the project root:
   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

   Or set them as environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN=your_bot_token_here
   export TELEGRAM_CHAT_ID=your_chat_id_here
   ```

4. **Test Notifications:**
   ```bash
   python -m src.ielts_monitor scan --cities tehran --exam-models cdielts
   ```

### Notification Features

- **Smart Tracking**: Only notifies about truly new slots, avoiding duplicates
- **State Persistence**: Remembers notified slots to prevent re-notifications
- **Auto-recovery**: If a slot gets filled and becomes available again, you'll be notified
- **Rich Messages**: Formatted notifications with all slot details
- **Error Handling**: Graceful handling of network issues and API limits

## Usage

The application provides a modern command-line interface with comprehensive monitoring capabilities.

### Command Structure

```bash
# Using uv (recommended)
uv run python -m src.ielts_monitor [options]

# Using python directly
python -m src.ielts_monitor [options]

# For help
uv run python -m src.ielts_monitor --help
```

### Examples

#### Continuous Monitoring (Default)

Start continuous monitoring with settings from config.yaml:
```bash
uv run python -m src.ielts_monitor
```

Monitor with custom check frequency (30 seconds):
```bash
uv run python -m src.ielts_monitor --check-frequency 30
```

Monitor specific cities and exam models:
```bash
uv run python -m src.ielts_monitor --cities tehran isfahan --exam-models cdielts
```

Show unavailable slots in the output:
```bash
uv run python -m src.ielts_monitor --show-unavailable
```

#### One-time Check

Run a single scan and exit:
```bash
uv run python -m src.ielts_monitor --once
```

Single scan with verbose logging:
```bash
uv run python -m src.ielts_monitor --once --verbose
```

#### Notification Management

Clear notification state (allows re-notification of all slots):
```bash
uv run python -m src.ielts_monitor --clear-notifications
```

Disable notifications:
```bash
uv run python -m src.ielts_monitor --no-notifications
```

### Command Line Options

All available options (use `--help` for full details):

**Monitoring Options:**
- `--cities`: Cities to check (e.g., `tehran isfahan`)
- `--exam-models`: Exam models to check (e.g., `cdielts pdielts`)
- `--months`: Months to check (1-12, e.g., `10 11`)
- `--check-frequency`: Check frequency in seconds (default: 3600)
- `--once`: Run a single check and exit
- `--verbose`: Enable verbose logging

**Display Options:**
- `--show-unavailable`: Show unavailable/filled slots in output

**Notification Options:**
- `--no-notifications`: Disable Telegram notifications
- `--clear-notifications`: Clear notification state (allows re-notification)

### Using Docker

Run with default settings from config.yaml:
```bash
docker run ielts-monitor
```

Run with custom options:
```bash
docker run ielts-monitor scan --cities tehran --exam-models cdielts --months 10 11 --show-unavailable
```

## 🖥️ Enhanced Terminal Output

The application features a professional, colorful terminal interface with real-time status updates:

### Key Features:
- **🎨 Beautiful Visual Design**: Professional formatting with emojis and colors
- **📊 Real-time Status**: Live updates on scanning, new slots, and notifications
- **⏰ Timestamps**: Precise timing for all activities
- **🔄 Activity Indicators**: Clear status for SCANNING, NOTIFICATIONS, WAITING
- **📋 Detailed Slot Information**: Complete appointment details with Persian support

### Example Output:
```
🚀 Starting IELTS appointment monitoring
🏙️  Monitoring cities: isfahan
📚 Monitoring exam models: cdielts
📅 Monitoring months: 10
🔔 Notifications enabled: ✅
⏱️  Check frequency: 3600 seconds

🔄 [15:27:15] SCANNING - Checking IELTS appointment availability...

============================================================
🎉 SLOTS FOUND: 2 available appointments
✨ 2 slots ready for immediate booking!
📋 UNAVAILABLE: 1 filled appointment
============================================================

🆕 NEW SLOT ALERT: 1 new appointment just became available!

🎯 Slot 1 Found:
   📅 Date: 2025-10-29 (۱۴۰۴/۰۹/۰۴)
   🕐 Time: صبح (۰۸:۳۰ - ۱۱:۳۰)
   📍 Location: اصفهان (ایده نواندیش)
   📝 Exam Type: cdielts - (Ac/Gt)
   💰 Price: ۲۹۱,۱۱۵,۰۰۰ ریال

🔄 [15:27:20] NOTIFICATIONS - Processing alerts for 2 available slots...
📤 NOTIFICATION SENT: Alert delivered for 2025-10-20 at اصفهان (ایده نواندیش)

🔄 [15:27:25] WAITING - Next scan in 3600 seconds
```

## Development

### Project Structure

The main implementation is contained in the root `run.py` file, which handles both monitoring and scanning functionality. The project also includes a `config.yaml` file for configuration.

```
ielts-monitoring2/
├── Dockerfile
├── README.md
├── config.yaml
└── run.py
```

### Key Features

- **Command-based Interface**: `monitor` for continuous checking and `scan` for one-time checks
- **Configuration System**: Reads from `config.yaml` with support for command-line overrides
- **Month Number Support**: Uses 1-12 instead of YYYY-MM format for month specification
- **URL Transparency**: Shows the exact URL being monitored
- **Text Cleaning**: Automatically processes Persian text in the output
- **Flexible Monitoring**: Customizable check frequency and notification options

### Testing

To test the application without making real HTTP requests, use the `--use-sample` flag with the `scan` command:

```bash
python run.py scan --use-sample --show-unavailable
```

This will use sample HTML data to demonstrate how the application processes and displays appointment slots.

## License

[MIT License](https://opensource.org/licenses/MIT)