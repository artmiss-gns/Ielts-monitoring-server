#!/usr/bin/env bash
# Test script for IELTS simulation server

echo "🧪 Testing IELTS Simulation Server"
echo "=================================="

# Check if server is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Server is running"
else
    echo "❌ Server is not running"
    echo "Please start the server first:"
    echo "cd simulation-server && python start_server.py"
    exit 1
fi

echo ""
echo "📋 Testing API endpoints..."

# Test health endpoint
echo "Testing /health..."
if curl -s http://localhost:8000/health | grep -q "OK"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
fi

# Test appointments endpoint
echo "Testing /api/appointments..."
APPOINTMENTS=$(curl -s http://localhost:8000/api/appointments)
if echo "$APPOINTMENTS" | grep -q "appointments"; then
    echo "✅ Appointments endpoint working"
    echo "Found $(echo "$APPOINTMENTS" | jq length) appointments"
else
    echo "❌ Appointments endpoint failed"
fi

# Test reset test data
echo "Testing /api/reset-test-data..."
if curl -s -X POST http://localhost:8000/api/reset-test-data | grep -q "success"; then
    echo "✅ Reset test data working"
else
    echo "❌ Reset test data failed"
fi

echo ""
echo "🌐 Testing web interface..."

# Test main page
echo "Testing /ielts/timetable..."
if curl -s http://localhost:8000/ielts/timetable | grep -q "IELTS Time Table"; then
    echo "✅ Main page accessible"
else
    echo "❌ Main page not accessible"
fi

echo ""
echo "📊 Testing monitoring system integration..."

# Test with sample data
echo "Testing monitoring with sample data..."
if python run.py scan --use-sample --base-url http://localhost:8000/ielts/timetable > /dev/null 2>&1; then
    echo "✅ Monitoring system works with simulation server"
else
    echo "❌ Monitoring system failed with simulation server"
fi

echo ""
echo "🎉 All tests completed!"
echo ""
echo "📍 Server URLs:"
echo "   Web Interface: http://localhost:8000/ielts/timetable"
echo "   API Docs: http://localhost:8000/docs"
echo "   Health: http://localhost:8000/health"
echo ""
echo "🚀 To start monitoring:"
echo "   python run.py monitor --base-url http://localhost:8000/ielts/timetable"
