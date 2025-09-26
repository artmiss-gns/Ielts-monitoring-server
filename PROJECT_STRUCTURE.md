# 📁 IELTS Monitor - Clean Project Structure

## 🎯 **Core Application** (Production Files)

```
src/ielts_monitor/           # Main application package
├── __main__.py             # Entry point (uv run python -m src.ielts_monitor)
├── config/                 # Configuration management
│   ├── __init__.py
│   └── settings.py        # YAML config loading, Pydantic models
├── notification/          # Telegram notification system
│   ├── __init__.py
│   ├── service.py        # Main notification service
│   └── http_sender.py    # HTTP fallback for Telegram
├── parser/               # HTML parsing and slot extraction
│   ├── __init__.py
│   └── availability.py  # Slot parsing logic
├── scraper/             # Website scraping
│   ├── __init__.py
│   └── client.py       # HTTP client for IELTS website
└── utils/              # Utilities and logging
    ├── __init__.py
    └── logger.py      # Enhanced logging with colors/emojis
```

## 📋 **Configuration & Setup**

```
config.yaml              # Main configuration (production-ready)
pyproject.toml          # Python project configuration (uv)
requirements.txt        # Dependencies
Dockerfile             # Container deployment
.gitignore            # Git ignore rules
```

## 📚 **Documentation**

```
README.md              # Main project documentation
docs/                 # Detailed documentation
├── README.md         # Documentation index
├── DEPLOYMENT_CHECKLIST.md  # Production deployment checklist
├── PRODUCTION_GUIDE.md      # Step-by-step deployment guide
├── FIXES_SUMMARY.md         # Development history
└── README-SIMULATION.md     # Simulation server docs
```

## 🧪 **Testing & Development**

```
tests/                # All test files and debugging scripts
├── README.md         # Testing documentation
├── test_*.py        # Various test scripts
├── debug_telegram.py # Telegram debugging
├── setup_telegram.py # Telegram setup helpers
└── test.ipynb       # Jupyter notebook for testing

samples/              # Sample HTML files for testing
├── README.md         # Sample files documentation
├── sample-html-page.html
├── sample-html-page2.html
└── sample-html-page-simulation.html
```

## 🔧 **Development Tools**

```
simulation-server/    # Local testing server
├── README.md         # Server documentation
├── server.py        # FastAPI simulation server
├── start_server.py  # Server startup script
├── requirements.txt # Server dependencies
├── data/
│   └── appointments.json  # Test appointment data
└── static/
    └── ielts-timetable.html  # HTML template

legacy/              # Deprecated files
├── README.md        # Legacy files documentation
└── run.py          # Old runner script (replaced)
```

## 🚀 **Quick Start Commands**

```bash
# Production monitoring
uv run python -m src.ielts_monitor

# Single scan
uv run python -m src.ielts_monitor --once

# Clear notifications
uv run python -m src.ielts_monitor --clear-notifications

# Start simulation server (for testing)
cd simulation-server && python start_server.py
```

## 🎯 **Key Benefits of This Structure**

✅ **Clean Separation**: Core app, tests, docs, samples all organized
✅ **Production Ready**: Only essential files in root directory
✅ **Easy Navigation**: Clear directory purposes with README files
✅ **Development Friendly**: All test/debug files in dedicated directories
✅ **Documentation**: Comprehensive guides for all use cases
✅ **Legacy Support**: Old files preserved but out of the way

## 📦 **Production Deployment**

For production, you only need:
- `src/` directory (core application)
- `config.yaml` (configuration)
- `pyproject.toml` & `requirements.txt` (dependencies)
- `.env` file (your Telegram credentials)

Everything else is for development, testing, and documentation.
