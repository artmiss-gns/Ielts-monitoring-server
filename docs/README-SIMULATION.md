# IELTS Monitoring System with Simulation Server

A comprehensive system for monitoring IELTS exam appointments with both real website scraping and simulation server capabilities.

## Features

- **Real-time Monitoring**: Monitor IELTS exam availability continuously
- **Simulation Server**: Test and develop without hitting the real website
- **Configurable URLs**: Switch between real and simulation modes easily
- **Multiple Cities**: Monitor appointments in different cities
- **Flexible Scheduling**: Check specific months and exam types
- **Rich Output**: Detailed information about available slots

## Quick Start

### Option 1: Using Simulation Server (Recommended for Testing)

1. **Start the simulation server:**
   ```bash
   cd simulation-server
   python start_server.py
   ```

2. **Update configuration to use simulation:**
   ```yaml
   # config.yaml
   base_url: 'http://localhost:8000'
   ```

3. **Run the monitor:**
   ```bash
   # Scan once
   python run.py scan

   # Continuous monitoring
   python run.py monitor
   ```

### Option 2: Using Real Website

1. **Update configuration for production:**
   ```yaml
   # config.yaml
   base_url: 'https://irsafam.org'
   ```

2. **Run the monitor:**
   ```bash
   python run.py monitor
   ```

## Configuration

Edit `config.yaml` to customize your monitoring:

```yaml
# Base URL for the IELTS website
base_url: 'http://localhost:8000'  # Use simulation server
# base_url: 'https://irsafam.org'   # Use real website

# Cities to monitor
cities:
  - isfahan
  - tehran
  - shiraz

# Exam types to check
exam_models:
  - cdielts  # Computer-delivered IELTS
  - pdielts  # Paper-delivered IELTS

# Months to check (1-12)
months:
  - 10  # October
  - 11  # November
  - 12  # December

# Check frequency in seconds (for continuous monitoring)
check_frequency: 3600  # 1 hour

# Show filled/unavailable slots
show_unavailable: false

# SSL verification (disable for testing)
no_ssl_verify: false
```

## Commands

### Monitor Continuously
```bash
python run.py monitor
```

### Scan Once
```bash
python run.py scan
```

### Command Line Options
```bash
# Monitor specific cities and exam types
python run.py monitor --cities isfahan tehran --exam-models cdielts

# Check specific months
python run.py scan --months 10 11 12

# Enable verbose logging
python run.py monitor --verbose

# Show unavailable slots
python run.py monitor --show-unavailable

# Use sample data for testing
python run.py scan --use-sample
```

## Simulation Server

The simulation server provides a realistic testing environment:

### Features
- **Dynamic Appointments**: Add/remove appointments via API
- **Realistic HTML**: Matches the structure of the real website
- **Interactive Controls**: Web interface for managing test data
- **Sample Data**: Pre-loaded with realistic test appointments

### API Endpoints
- `GET /api/appointments` - List all appointments
- `POST /api/appointments` - Create new appointment
- `PUT /api/appointments/{id}` - Update appointment
- `DELETE /api/appointments/{id}` - Delete appointment
- `POST /api/reset-test-data` - Reset to sample data
- `GET /ielts/timetable` - Main timetable page

### Managing Test Data

```bash
# Reset to sample data
curl -X POST http://localhost:8000/api/reset-test-data

# Add a new appointment
curl -X POST http://localhost:8000/api/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-12-01",
    "time": "صبح (۰۹:۰۰ - ۱۲:۰۰)",
    "location": "تهران (مرکز جدید)",
    "city": "Tehran",
    "examType": "cdielts - (Ac/Gt)",
    "price": "۲۹۱,۱۱۵,۰۰۰ ریال",
    "persianDate": "۱۴۰۴/۰۹/۱۰",
    "status": "available"
  }'

# Clear all appointments
curl -X DELETE http://localhost:8000/api/appointments
```

## Output Format

### Available Slots
```
📅 2 appointments found:
  ✅ 2 Available
  ❌ 0 Unavailable

--------------------------------------------------
✅ Available slots:
--------------------------------------------------
  • 2025-11-10 | PM (۱۳:۳۰ - ۱۶:۳۰) | اصفهان (ایده نواندیش) | ۲۹۱,۱۱۵,۰۰۰ ریال
  • 2025-11-17 | AM (۰۹:۰۰ - ۱۲:۰۰) | تهران (مرکز آزمون) | ۲۹۱,۱۱۵,۰۰۰ ریال
```

### Unavailable Slots (when enabled)
```
--------------------------------------------------
❌ Unavailable slots:
--------------------------------------------------
  • 2025-10-27 | PM (۱۳:۳۰ - ۱۶:۳۰) | اصفهان (ایده نواندیش)
  • 2025-11-03 | AM (۰۹:۰۰ - ۱۲:۰۰) | اصفهان (ایده نواندیش)
```

## Testing

Run the test script to verify everything works:

```bash
python test_simulation.py
```

This will test:
- Server connectivity
- API endpoints
- Web interface
- Monitoring system integration

## Troubleshooting

### Common Issues

1. **No appointments found**
   - Check your internet connection (for real website)
   - Verify the simulation server is running (for testing)
   - Ensure cities and exam types are spelled correctly

2. **SSL certificate errors**
   - Enable `no_ssl_verify: true` in config.yaml for testing
   - This is normal for some development environments

3. **Port conflicts**
   - Change the simulation server port in `start_server.py`
   - Default is 8000

4. **Permission errors**
   - Ensure you have write permissions for data directories
   - Run as administrator if needed

### Debug Mode

Enable verbose logging for detailed information:

```bash
python run.py monitor --verbose
```

## Project Structure

```
├── config.yaml                 # Configuration file
├── run.py                      # Main monitoring script
├── simulation-server/          # FastAPI simulation server
│   ├── server.py              # Main server application
│   ├── start_server.py        # Server startup script
│   ├── requirements.txt       # Python dependencies
│   ├── static/               # Static web files
│   │   └── ielts-timetable.html
│   ├── data/                 # Appointment data
│   │   └── appointments.json
│   └── README.md             # Server documentation
├── sample-html-page-simulation.html  # Sample HTML for testing
└── test_simulation.py        # Test script
```

## Development

### Adding New Features

1. **Parser Updates**: Modify the `AvailabilityParser` class in `run.py`
2. **New Exam Types**: Add to the `exam_models` list in config
3. **Additional Cities**: Add to the `cities` list in config
4. **Custom Output**: Modify the output formatting in `run_monitor()`

### Contributing

1. Test changes with the simulation server first
2. Ensure compatibility with both real and simulation modes
3. Update documentation for any new features
4. Add appropriate error handling

## License

This project is for educational and testing purposes. Please respect the terms of service of the real IELTS website when using in production mode.
