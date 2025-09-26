# IELTS Monitoring Simulation Server

This directory contains a FastAPI-based simulation server for testing the IELTS monitoring system. The server mimics the real IELTS website structure and allows for dynamic appointment management.

## Features

- **FastAPI Backend**: Modern, fast web framework with automatic API documentation
- **Dynamic Appointments**: Add, remove, update, and clear appointments via API
- **Realistic HTML**: Serves HTML that matches the structure of the real IELTS website
- **Sample Data**: Pre-loaded with test appointments (both available and filled)
- **Interactive Controls**: Web interface with buttons to manage appointments
- **Filtering**: Filter appointments by city, status, and month

## Quick Start

### 1. Install Dependencies

```bash
cd simulation-server
pip install -r requirements.txt
```

### 2. Start the Server

```bash
# Option 1: Using the startup script
python start_server.py

# Option 2: Direct uvicorn command
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the Server

- **Web Interface**: http://localhost:8000/ielts/timetable
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## API Endpoints

### Appointments Management

- `GET /api/appointments` - Get all appointments
- `POST /api/appointments` - Create a new appointment
- `PUT /api/appointments/{id}` - Update an existing appointment
- `DELETE /api/appointments/{id}` - Delete a specific appointment
- `DELETE /api/appointments` - Clear all appointments
- `POST /api/reset-test-data` - Reset to default sample data

### Other Endpoints

- `GET /health` - Health check
- `GET /ielts/timetable` - Main timetable page

## Configuration

### Using with Monitoring System

To use the simulation server with the monitoring system, update your `config.yaml`:

```yaml
# Configuration for IELTS appointment monitoring

# Base URL for the IELTS website (use 'localhost' for simulation server)
# Options: 'https://irsafam.org' (real website) or 'http://localhost:8000' (simulation server)
base_url: 'http://localhost:8000'

cities:
  - isfahan
  - tehran

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

### Running the Monitor with Simulation

```bash
# Scan once using simulation server
python run.py scan --use-sample

# Continuous monitoring using simulation server
python run.py monitor --base-url http://localhost:8000/ielts/timetable
```

## Sample Data Structure

The server comes with pre-loaded sample appointments:

```json
{
  "id": "available-1",
  "date": "2025-11-10",
  "time": "ظهر (۱۳:۳۰ - ۱۶:۳۰)",
  "location": "اصفهان (ایده نواندیش)",
  "city": "Isfahan",
  "examType": "cdielts - (Ac/Gt)",
  "price": "۲۹۱,۱۱۵,۰۰۰ ریال",
  "persianDate": "۱۴۰۴/۰۸/۱۹",
  "status": "available",
  "filledIndicators": [],
  "availableIndicators": ["قابل ثبت نام", "active-button"],
  "registrationUrl": "http://localhost:8000/ielts/register/available-1"
}
```

## Web Interface

The web interface at `/ielts/timetable` provides:

- **Real-time Updates**: Appointments update automatically every 30 seconds
- **Interactive Controls**: Buttons to refresh, reset data, clear all, and add random appointments
- **Filtering**: Filter by city, status, and month
- **Visual Indicators**: Color-coded status indicators for available/filled slots
- **Responsive Design**: Works on desktop and mobile devices

## Development

### Adding New Features

1. **API Changes**: Modify `server.py` and update the Pydantic models
2. **Frontend Changes**: Update `static/ielts-timetable.html`
3. **Data Models**: Update the `Appointment` and `AppointmentCreate` classes

### Testing

```bash
# Test API endpoints
curl http://localhost:8000/api/appointments

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
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**: Change the port in `start_server.py` or use a different port
2. **Dependencies Not Installed**: Run `pip install -r requirements.txt`
3. **Permission Issues**: Make sure you have write permissions for the data directory

### Logs

Server logs are displayed in the terminal. For more detailed logging:

```bash
export LOG_LEVEL=DEBUG
python start_server.py
```

## Integration with Real Monitoring

To switch between simulation and real website:

1. **Simulation Mode**: Set `base_url: 'http://localhost:8000'` in config.yaml
2. **Production Mode**: Set `base_url: 'https://irsafam.org'` in config.yaml

The monitoring system will automatically use the configured URL for all requests.
