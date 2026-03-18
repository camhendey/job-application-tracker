import pandas as pd
import os
from datetime import datetime

CSV_FILE = "applications.csv"

COLUMNS = [
    "Company",
    "Role",
    "Date Applied",
    "Source",
    "Status",
    "Notes",
    "Contact Name",
    "Contact LinkedIn",
]

STATUSES = [
    "Applied",
    "Follow-Up Sent",
    "Interview Scheduled",
    "Offer",
    "Rejected",
    "Ghosted",
]

SOURCES = [
    "LinkedIn",
    "Company Website",
    "Referral",
    "Cold Outreach",
    "Job Board",
    "Recruiter",
    "Other",
]


def load_applications() -> pd.DataFrame:
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, parse_dates=["Date Applied"])
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df
    return pd.DataFrame(columns=COLUMNS)


def save_applications(df: pd.DataFrame) -> None:
    df.to_csv(CSV_FILE, index=False)


def add_application(
    company: str,
    role: str,
    date_applied: datetime,
    source: str,
    status: str,
    notes: str,
    contact_name: str,
    contact_linkedin: str,
) -> pd.DataFrame:
    df = load_applications()
    new_row = pd.DataFrame(
        [
            {
                "Company": company,
                "Role": role,
                "Date Applied": date_applied,
                "Source": source,
                "Status": status,
                "Notes": notes,
                "Contact Name": contact_name,
                "Contact LinkedIn": contact_linkedin,
            }
        ]
    )
    df = pd.concat([df, new_row], ignore_index=True)
    save_applications(df)
    return df


def update_application(index: int, updates: dict) -> pd.DataFrame:
    df = load_applications()
    for key, value in updates.items():
        if key in df.columns:
            df.at[index, key] = value
    save_applications(df)
    return df


def days_since_applied(date_applied) -> int:
    if pd.isna(date_applied):
        return 0
    if isinstance(date_applied, str):
        date_applied = pd.to_datetime(date_applied)
    return (datetime.now() - date_applied).days


def needs_follow_up(row) -> bool:
    return row["Status"] == "Applied" and days_since_applied(row["Date Applied"]) > 7
