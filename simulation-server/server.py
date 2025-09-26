#!/usr/bin/env python3
"""
FastAPI simulation server for IELTS monitoring testing.
This server mimics the real IELTS website structure and allows adding/removing appointments.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="IELTS Test Simulation Server",
    description="Simulation server for testing IELTS monitoring system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Appointment(BaseModel):
    id: str
    date: str
    time: str
    location: str
    city: str
    examType: str
    price: str
    persianDate: str
    status: str
    filledIndicators: List[str] = []
    availableIndicators: List[str] = []
    registrationUrl: Optional[str] = None

class AppointmentCreate(BaseModel):
    date: str
    time: str
    location: str
    city: str
    examType: str
    price: str
    persianDate: str
    status: str = "available"
    filledIndicators: List[str] = []
    availableIndicators: List[str] = []
    registrationUrl: Optional[str] = None

# Data file path
DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "appointments.json"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

def read_appointments() -> List[Dict[str, Any]]:
    """Read appointments from JSON file."""
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def write_appointments(appointments: List[Dict[str, Any]]) -> None:
    """Write appointments to JSON file."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(appointments, f, indent=2, ensure_ascii=False)

def create_sample_data() -> List[Dict[str, Any]]:
    """Create sample appointment data."""
    return [
        {
            "id": "filled-1",
            "date": "2025-10-27",
            "time": "ظهر (۱۳:۳۰ - ۱۶:۳۰)",
            "location": "اصفهان (ایده نواندیش)",
            "city": "Isfahan",
            "examType": "cdielts - (Ac/Gt)",
            "price": "۲۹۱,۱۱۵,۰۰۰ ریال",
            "persianDate": "۱۴۰۴/۰۸/۰۵",
            "status": "filled",
            "filledIndicators": ["disabled", "تکمیل ظرفیت"],
            "registrationUrl": None
        },
        {
            "id": "filled-2",
            "date": "2025-11-03",
            "time": "صبح (۰۹:۰۰ - ۱۲:۰۰)",
            "location": "اصفهان (ایده نواندیش)",
            "city": "Isfahan",
            "examType": "cdielts - (Ac/Gt)",
            "price": "۲۹۱,۱۱۵,۰۰۰ ریال",
            "persianDate": "۱۴۰۴/۰۸/۱۲",
            "status": "filled",
            "filledIndicators": ["disabled", "تکمیل ظرفیت"],
            "registrationUrl": None
        },
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
        },
        {
            "id": "available-2",
            "date": "2025-11-17",
            "time": "صبح (۰۹:۰۰ - ۱۲:۰۰)",
            "location": "تهران (مرکز آزمون)",
            "city": "Tehran",
            "examType": "cdielts - (Ac/Gt)",
            "price": "۲۹۱,۱۱۵,۰۰۰ ریال",
            "persianDate": "۱۴۰۴/۰۸/۲۶",
            "status": "available",
            "filledIndicators": [],
            "availableIndicators": ["قابل ثبت نام", "active-button"],
            "registrationUrl": "http://localhost:8000/ielts/register/available-2"
        }
    ]

# API Routes

@app.get("/api/appointments")
async def get_appointments():
    """Get all appointments."""
    return read_appointments()

@app.post("/api/appointments")
async def create_appointment(appointment: AppointmentCreate):
    """Create a new appointment."""
    appointments = read_appointments()

    # Generate ID if not provided
    new_id = appointment.dict()
    if 'id' not in new_id:
        new_id['id'] = str(uuid.uuid4())

    appointments.append(new_id)
    write_appointments(appointments)

    return new_id

@app.put("/api/appointments/{appointment_id}")
async def update_appointment(appointment_id: str, appointment: AppointmentCreate):
    """Update an existing appointment."""
    appointments = read_appointments()

    for i, apt in enumerate(appointments):
        if apt['id'] == appointment_id:
            updated_apt = appointment.dict()
            updated_apt['id'] = appointment_id
            appointments[i] = updated_apt
            write_appointments(appointments)
            return updated_apt

    raise HTTPException(status_code=404, detail="Appointment not found")

@app.delete("/api/appointments/{appointment_id}")
async def delete_appointment(appointment_id: str):
    """Delete a specific appointment."""
    appointments = read_appointments()

    for i, apt in enumerate(appointments):
        if apt['id'] == appointment_id:
            deleted_apt = appointments.pop(i)
            write_appointments(appointments)
            return deleted_apt

    raise HTTPException(status_code=404, detail="Appointment not found")

@app.delete("/api/appointments")
async def clear_all_appointments():
    """Clear all appointments."""
    write_appointments([])
    return {"message": "All appointments cleared"}

@app.post("/api/reset-test-data")
async def reset_test_data():
    """Reset appointments to default test data."""
    sample_data = create_sample_data()
    write_appointments(sample_data)
    return {"message": "Test data reset successfully", "count": len(sample_data)}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "OK", "timestamp": datetime.now().isoformat()}

@app.get("/api/appointments/search")
async def search_appointments(city: str = None, status: str = None, exam_type: str = None):
    """Search appointments with filters."""
    appointments = read_appointments()

    filtered = appointments
    if city:
        filtered = [apt for apt in filtered if apt["city"].lower() == city.lower()]
    if status:
        filtered = [apt for apt in filtered if apt["status"] == status]
    if exam_type:
        filtered = [apt for apt in filtered if apt["examType"] == exam_type]

    return {"appointments": filtered, "count": len(filtered)}

@app.get("/api/statistics")
async def get_statistics():
    """Get appointment statistics."""
    appointments = read_appointments()

    total = len(appointments)
    available = len([apt for apt in appointments if apt["status"] == "available"])
    filled = len([apt for apt in appointments if apt["status"] == "filled"])

    cities = {}
    for apt in appointments:
        city = apt["city"]
        if city not in cities:
            cities[city] = {"total": 0, "available": 0, "filled": 0}
        cities[city]["total"] += 1
        if apt["status"] == "available":
            cities[city]["available"] += 1
        else:
            cities[city]["filled"] += 1

    return {
        "total": total,
        "available": available,
        "filled": filled,
        "by_city": cities
    }

@app.get("/api/cities")
async def get_cities():
    """Get list of available cities."""
    appointments = read_appointments()
    cities = list(set(apt["city"] for apt in appointments))
    return {"cities": sorted(cities)}

@app.get("/api/exam-types")
async def get_exam_types():
    """Get list of available exam types."""
    appointments = read_appointments()
    exam_types = list(set(apt["examType"] for apt in appointments))
    return {"exam_types": sorted(exam_types)}

@app.get("/api/appointments/{appointment_id}")
async def get_appointment(appointment_id: str):
    """Get a specific appointment by ID."""
    appointments = read_appointments()

    for apt in appointments:
        if apt["id"] == appointment_id:
            return apt

    raise HTTPException(status_code=404, detail="Appointment not found")

# Serve static HTML files
@app.get("/ielts/timetable", response_class=HTMLResponse)
async def get_ielts_timetable():
    """Serve the IELTS timetable page with pre-rendered appointments."""
    appointments = read_appointments()

    # Generate HTML for appointments
    appointments_html = ""
    for apt in appointments:
        status_class = "available" if apt["status"] == "available" else "filled"
        disabled_class = "disabled" if apt["status"] == "filled" else ""
        status_text = "قابل ثبت نام" if apt["status"] == "available" else "تکمیل ظرفیت"

        # Build onclick attribute
        if apt["status"] == "filled":
            onclick_attr = 'onclick="return false"'
        else:
            onclick_attr = 'onclick="registerAppointment(event, \'{}\')"'.format(apt["id"])

        appointments_html += f'''
            <a href="{apt.get("registrationUrl", "#")}" class="exam__item ielts {status_class} {disabled_class}" {onclick_attr}>
                <div class="status-indicator status-{apt["status"]}">{status_text}</div>
                <div class="exam__title">
                    <h5>{apt["location"]}</h5>
                </div>
                <div class="exam__date">
                    <time>
                        <span>{apt["date"]}</span>
                        <span class="farsi_date">{apt["persianDate"]}</span>
                    </time>
                </div>
                <div class="exam__time">
                    {apt["time"]}
                </div>
                <div class="exam__details">
                    <span class="exam__type">{apt["examType"]}</span>
                </div>
                <div class="exam__price">
                    {apt["price"]}
                </div>
                <div class="exam__buttons">
                    {"".join(f'<button class="btn btn-primary">{indicator}</button>' for indicator in apt.get("availableIndicators", []))}
                    {"".join(f'<button class="btn" disabled>{indicator}</button>' for indicator in apt.get("filledIndicators", []))}
                </div>
            </a>
        '''

    # Read the HTML template and replace the loading div
    html_file = Path(__file__).parent / "static" / "ielts-timetable.html"
    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        # Replace the loading container with actual appointments
        html_content = html_content.replace('<div id="exams-container" class="exams-grid">\n            <div class="loading">Loading appointments...</div>\n        </div>',
                                          f'<div id="exams-container" class="exams-grid">\n            {appointments_html}\n        </div>')
        return HTMLResponse(content=html_content)

    # Fallback: return simple HTML if template doesn't exist
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IELTS Time Table - Simulation</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; direction: rtl; }}
            .exam__item {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
            .available {{ border-color: #28a745; background-color: #f8fff8; }}
            .filled {{ border-color: #dc3545; background-color: #fff8f8; }}
        </style>
    </head>
    <body>
        <h1>IELTS Time Table - Simulation Server</h1>
        <div id="exams-container">
            {appointments_html}
        </div>
    </body>
    </html>
    """)

# Catch-all route for SPA-like behavior
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(request: Request):
    """Catch-all route for SPA-like behavior."""
    # Try to serve static files first
    static_file = Path(__file__).parent / "static" / request.path_params["full_path"]
    if static_file.exists() and static_file.is_file():
        return FileResponse(static_file)

    # Return main page for other routes
    return await get_ielts_timetable()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting IELTS Test Simulation Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📋 API endpoints:")
    print("   GET  /api/appointments           - Get all appointments")
    print("   GET  /api/appointments/{id}      - Get specific appointment")
    print("   GET  /api/appointments/search   - Search with filters")
    print("   GET  /api/statistics            - Get appointment statistics")
    print("   GET  /api/cities                - Get available cities")
    print("   GET  /api/exam-types            - Get available exam types")
    print("   POST /api/appointments           - Create new appointment")
    print("   PUT  /api/appointments/{id}      - Update appointment")
    print("   DELETE /api/appointments/{id}    - Delete appointment")
    print("   DELETE /api/appointments         - Clear all appointments")
    print("   POST /api/reset-test-data        - Reset to sample data")
    print("   GET  /health                     - Health check")
    print("   GET  /ielts/timetable            - IELTS timetable page")
    print("   GET  /docs                       - API documentation")
    print("\nPress Ctrl+C to stop the server")

    uvicorn.run(app, host="0.0.0.0", port=8000)
