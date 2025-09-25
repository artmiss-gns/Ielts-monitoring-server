# IELTS Monitoring

A lightweight application that monitors the Irsafam website (https://irsafam.org/ielts/timetable) for available IELTS exam slots. This tool provides a simple and efficient way to track IELTS appointment availability across different cities and exam types.

## Features

- **Command-based Interface**: Two main commands - `monitor` for continuous tracking and `scan` for one-time checks
- **Configuration System**: Uses YAML configuration file for easy setup (reads from config.yaml by default)
- **Month Number Support**: Simplified month selection using numbers (1-12) instead of YYYY-MM format
- **Enhanced Readability**: Persian text cleaning for clearer output and emoji indicators
- **URL Transparency**: Shows URLs being accessed for monitoring
- **Resource-efficient Implementation**: No headless browsers required
- **Responsible Scraping**: Configurable delays to respect website limits
- **Containerized**: For easy deployment (Dockerfile included)

## Installation

### Using Python

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd ielts-monitoring2
   ```

2. Install the required dependencies:
   ```bash
   pip install pyyaml requests beautifulsoup4
   ```

   Alternatively, we recommend using [uv](https://github.com/astral-sh/uv) for faster installation:
   ```bash
   uv pip install pyyaml requests beautifulsoup4
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

## Usage

The application provides two main commands: `monitor` for continuous monitoring and `scan` for a one-time check.

### Command Structure

```
usage: python run.py {monitor,scan} [options]

# For help with a specific command
python run.py monitor --help
python run.py scan --help
```

### Examples

#### Using the `monitor` Command (Continuous Monitoring)

Start continuous monitoring with settings from config.yaml:
```bash
python run.py monitor
```

Run with a custom check frequency (in seconds):
```bash
python run.py monitor --check-frequency 1800
```

Monitor specific cities and exam models (overrides config):
```bash
python run.py monitor --cities tehran isfahan --exam-models cdielts
```

Show unavailable slots in the output:
```bash
python run.py monitor --show-unavailable
```

Disable SSL certificate verification (useful if encountering SSL issues):
```bash
python run.py monitor --no-ssl-verify
```

#### Using the `scan` Command (One-time Check)

Run a one-time scan with settings from config.yaml:
```bash
python run.py scan
```

Scan specific cities, exam models, and months (overrides config):
```bash
python run.py scan --cities tehran --exam-models cdielts --months 10 11 12
```

Use sample data for testing (no actual website requests):
```bash
python run.py scan --use-sample
```

Show all slots including unavailable ones:
```bash
python run.py scan --use-sample --show-unavailable
```

### Command Line Options

Both commands support these options (check `--help` for full details):
- `--cities`: Cities to check (e.g., tehran isfahan)
- `--exam-models`: Exam models to check (e.g., cdielts pdielts)
- `--months`: Months to check (1-12, e.g., 10 11)
- `--check-frequency`: Check frequency in seconds (monitor command only)
- `--show-unavailable`: Show unavailable/filled slots
- `--no-ssl-verify`: Disable SSL certificate verification
- `--use-sample`: Use sample data (scan command only)

### Using Docker

Build the Docker image:
```bash
docker build -t ielts-monitor .
```

Run with default settings from config.yaml:
```bash
docker run ielts-monitor
```

Run with custom options:
```bash
docker run ielts-monitor scan --cities tehran --exam-models cdielts --months 10 11 --show-unavailable

## Output Format

The application displays appointment slots in a clear, organized format. Key features of the output:

- Shows the URL being monitored at the start of the process
- Groups slots by date for easy viewing
- Available slots are marked with [✅ Available]
- Unavailable slots are marked with [❌ Unavailable] (when using `--show-unavailable`)
- Persian text in time of day and location is automatically cleaned and simplified
- Shows check frequency and next check time in a user-friendly format

Example output:
```
Monitoring URL: https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=cdielts&month%5B%5D=2025-10
Checking again in 10 seconds...

No available slots found.

--------------------------------------------------
Found 56 unavailable/filled slots:
--------------------------------------------------

Date: 11 Oct 2025
  ├── Afternoon (13:30 - 16:30) - Isfahan (Ideh Nowandish) (cdielts - (Ac/Gt)) [❌ Unavailable]
  └── Price: 291,115,000 Rial
  ├── Morning (08:30 - 11:30) - Isfahan (Ideh Nowandish) (cdielts - (Ac/Gt)) [❌ Unavailable]
  └── Price: 291,115,000 Rial

Date: 18 Oct 2025
  ├── Afternoon (13:30 - 16:30) - Tehran (Pars) (cdielts - (Ac/Gt)) [✅ Available]
  └── Price: 291,115,000 Rial
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