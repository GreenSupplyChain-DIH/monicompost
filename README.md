# MoniCompost

Analyze compost pile telemetry and turn it into practical, day-to-day recommendations.

MoniCompost ingests sensor data (e.g., temperature, moisture, oxygen), evaluates compost health, and provides actionable guidance to help maintain optimal decomposition conditions. It can also integrate recommendations with farm calendar workflows.

---

## Features

- **Telemetry ingestion** for compost pile sensor streams
- **Health analysis** based on compost process signals
- **Actionable recommendations** (turn pile, add water, add dry carbon, etc.)
- **Optional farm calendar integration** to schedule interventions
- **Container-friendly deployment** with Docker support
- **Template-driven reporting/output** (Mako)

---

## Quick Start

### Prerequisites

- Python 3.10+ (recommended)
- `pip` (or your preferred Python package manager)
- Optional: Docker

### 1) Clone the repository

```bash
git clone https://github.com/fedjo/monicompost.git
cd monicompost
```

### 2) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows PowerShell
```

### 3) Install dependencies

If your project uses a requirements file:

```bash
pip install -r requirements.txt
```

If you use `pyproject.toml`, install accordingly (example):

```bash
pip install -e .
```

### 4) Configure environment

Create a local environment file (example):

```bash
cp .env.example .env
```

Set values for data sources, thresholds, and optional calendar integration credentials.

### 5) Run MoniCompost

Use your project’s main entrypoint (examples):

```bash
python -m monicompost
# or
python scripts/run_analysis.py
```

### 6) Run with Docker (optional)

Build and run:

```bash
docker build -t monicompost:latest .
docker run --rm --env-file .env monicompost:latest
```

If your workflow needs mounted files (e.g., configs/reports), add `-v` mounts accordingly.

---

## Example Recommendation Output

MoniCompost may produce recommendations like:

- “Temperature has remained above 68°C for 3 hours — **turn pile within 12 hours**.”
- “Moisture trend is below target — **add water (~15–20 L) and recheck in 4 hours**.”
- “Oxygen recovery is slow after turning — **increase bulking agent ratio**.”

---

## Roadmap Ideas

- Adaptive thresholding from historical pile behavior
- Recommendation confidence scoring
- Multi-pile dashboarding
- Native integrations with additional farm management systems
- SMS/WhatsApp alert channels

---

## Contributing

Contributions are welcome. Please open an issue or pull request with:

1. Problem statement
2. Proposed change
3. Testing notes

---

## License

Licensed under Apache-2.0
