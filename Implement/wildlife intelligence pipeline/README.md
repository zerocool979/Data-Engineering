# 🌿 Wildlife Intelligence Monitoring System (WIMS)

> A modern, full-stack Data Engineering platform for wildlife conservation analytics — built with Python, FastAPI, SQLite, and Streamlit.

---

## Overview

**WIMS** is a production-grade data engineering platform designed to ingest, process, analyze, and export wildlife datasets. It features a full ETL pipeline with automated data cleaning, feature engineering, a REST API backend, and an interactive dark-mode dashboard.

Built for researchers, conservationists, and data engineers who need reliable, automated tooling for biodiversity monitoring.

---

## Features

| Feature | Description |
|---|---|
| 📊 **Dashboard** | Real-time KPIs, 10+ interactive Plotly charts |
| 📁 **Upload & Pipeline** | Auto ETL: Validate → Clean → Engineer → Load |
| 🔍 **Search Engine** | Multi-field real-time filtering |
| ✏️ **CRUD Manager** | Full Create/Read/Update/Delete for animal records |
| 📤 **Export Center** | CSV, JSON, Excel, Parquet, SQL Dump |
| 🔧 **Feature Engineering** | Risk Score, Size/Speed Category, Survival Probability |
| 📋 **Pipeline Logs** | DB + file-based activity logging |
| 🔌 **REST API** | FastAPI with /animals, /upload, /analytics, /export, /search |

---

## Architecture

```
wims/
├── backend/           # FastAPI REST API
│   ├── database/      # SQLAlchemy models & connection
│   └── routes/        # animals, upload, analytics, export, search
├── dashboard/         # Streamlit UI
│   └── app.py         # Main multi-page dashboard
├── pipeline/          # ETL modules
│   ├── cleaner.py     # Data cleaning
│   ├── validator.py   # Schema & quality validation
│   ├── feature_engineering.py  # Derived features
│   ├── exporter.py    # Multi-format export
│   └── pipeline_runner.py      # ETL orchestrator
├── data/
│   ├── master/        # Authoritative source CSVs
│   ├── uploads/       # User-uploaded files
│   ├── processed/     # Intermediate outputs
│   └── exports/       # Generated export files
└── logs/              # pipeline.log
```

---

## Tech Stack

- **Frontend**: Streamlit + custom CSS (dark mode) + Plotly
- **Backend**: FastAPI + Uvicorn
- **Database**: SQLite + SQLAlchemy ORM
- **Data Engineering**: Pandas + NumPy
- **Export**: openpyxl, xlsxwriter, pyarrow

---

## Installation

### 1. Clone or extract the project

```bash
cd wims
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run (loads data + launches dashboard)

```bash
python run.py
```

Open **http://localhost:8501** in your browser.

To also start the API server:
```bash
python run.py --api
# API docs at http://localhost:8000/docs
```

---

## API Documentation

| Endpoint | Method | Description |
|---|---|---|
| `GET /animals/` | GET | List all animals (paginated) |
| `GET /animals/{id}` | GET | Get animal by ID |
| `POST /animals/` | POST | Create new animal |
| `PUT /animals/{id}` | PUT | Update animal |
| `DELETE /animals/{id}` | DELETE | Soft-delete animal |
| `POST /upload/` | POST | Upload CSV + run pipeline |
| `GET /upload/history` | GET | Upload history |
| `GET /analytics/summary` | GET | Dashboard KPIs |
| `GET /analytics/conservation` | GET | Conservation distribution |
| `GET /analytics/habitat` | GET | Habitat distribution |
| `GET /analytics/speed` | GET | Speed rankings |
| `GET /analytics/risk` | GET | Top risk animals |
| `GET /export/{format}` | GET | Export data (csv/json/xlsx/parquet/sql) |
| `GET /search/` | GET | Search with filters |

---

## Database Schema

```sql
CREATE TABLE animals (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    height_cm TEXT, weight_kg TEXT, color TEXT,
    lifespan_years TEXT, diet TEXT, habitat TEXT,
    predators TEXT, top_speed_kmh REAL,
    countries_found TEXT, conservation_status TEXT,
    family TEXT, gestation_period_days TEXT,
    social_structure TEXT, offspring_per_birth TEXT,
    -- Engineered features
    size_category TEXT, speed_category TEXT,
    risk_score REAL, endangered_level INTEGER,
    survival_probability REAL,
    -- Metadata
    source_file TEXT, is_active BOOLEAN,
    created_at DATETIME, updated_at DATETIME
);

CREATE TABLE uploads (
    id INTEGER PRIMARY KEY,
    filename TEXT, rows_total INTEGER,
    rows_inserted INTEGER, rows_duplicate INTEGER,
    quality_score REAL, status TEXT,
    uploaded_at DATETIME
);

CREATE TABLE pipeline_logs (
    id INTEGER PRIMARY KEY,
    pipeline_name TEXT, stage TEXT,
    level TEXT, message TEXT,
    created_at DATETIME
);
```

---

## Feature Engineering

| Feature | Logic |
|---|---|
| `speed_category` | Slow (<20), Moderate (<50), Fast (<80), Very Fast (80+) |
| `size_category` | Tiny (<5kg), Small (<50kg), Medium (<300kg), Large (<2000kg), Giant |
| `endangered_level` | 1–7 based on IUCN status |
| `risk_score` | Composite: 60% endangerment + 20% speed + 20% size |
| `survival_probability` | 1 - (risk/100) ± social structure bonus |

---

## Future Improvements

- [ ] Map visualization (GeoPandas / Folium) for country distribution
- [ ] Time-series tracking of population trends
- [ ] ML-based extinction risk prediction
- [ ] User authentication & multi-tenant support
- [ ] Docker Compose deployment
- [ ] Scheduled pipeline runs (Apache Airflow integration)
- [ ] Email alerts for critically endangered status changes
