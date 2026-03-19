## Job Application Tracker

This is a Streamlit-based dashboard for tracking your job applications. It lets you:
- Log new applications with status, source, and contact info.
- Update existing applications as you move through the process.
- View filters, metrics, and charts that summarize your pipeline.

### AI Outreach Message Integration

The app includes an **AI Outreach Helper** that can draft a tailored outreach message for a selected application:
- It uses the `generate_outreach_message` helper in `ai_helpers.py`.
- The helper calls the OpenAI Chat Completions API to generate a short, professional message.
- The message is shown in a text area so you can review and edit it before sending from your own email or LinkedIn account.

To enable the AI feature:
1. Install dependencies from `requirements.txt`.
2. Set the `OPENAI_API_KEY` environment variable to a valid OpenAI API key.
3. Run the app with:

```bash
streamlit run app.py
```

If `OPENAI_API_KEY` is not set, the AI Outreach Helper will display a clear error instead of generating a message.

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
