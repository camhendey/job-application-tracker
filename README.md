# Job Application Tracker

A lightweight personal dashboard for managing and monitoring your job search, built with Python and Streamlit.

## Features

- **Log applications** with company, role, date, source, status, notes, and contact info
- **Update status** on any existing application as things progress
- **Dashboard metrics** — total apps, active apps, response rate, weekly count, average days waiting
- **Filterable table** — filter by status, sort by date, search by company name, colour-coded rows
- **Follow-up flags** — applications sitting in *Applied* for 7+ days are automatically flagged

## Tech Stack

- **Python** — core language
- **Streamlit** — UI and dashboard
- **pandas** — CSV read/write, filtering, sorting

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`. An `applications.csv` file is created automatically in the project folder when you log your first application.

## File Structure

```
job-application-tracker/
├── app.py                 # Main Streamlit app
├── tracker.py             # CSV read/write logic
├── applications.csv       # Local data storage (auto-created)
├── .gitignore
├── requirements.txt
└── README.md
```

## Data Storage

All data lives in a single `applications.csv` file — no database, no backend, no login. Simple and portable.
