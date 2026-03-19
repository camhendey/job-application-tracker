import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from tracker import (
    load_applications,
    add_application,
    update_application,
    days_since_applied,
    needs_follow_up,
    STATUSES,
    SOURCES,
)

#NEW
from ai_helpers import generate_outreach_message  # helper that calls the OpenAI API to draft outreach text

st.set_page_config(page_title="Job Application Tracker", page_icon="📋", layout="wide")  # must be first Streamlit command

# Centralised status → colour mapping so UI stays consistent across the app
STATUS_COLOURS = {
    "Applied": "#3b82f6",
    "Follow-Up Sent": "#f59e0b",
    "Interview Scheduled": "#8b5cf6",
    "Offer": "#10b981",
    "Rejected": "#ef4444",
    "Ghosted": "#6b7280",
}

# Global page-level styling for metric cards, status pills, and flags
st.markdown(
    """
    <style>
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        text-align: center;
    }
    .metric-card h3 {
        margin: 0 0 0.3rem 0;
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card p {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
    }
    .flag-badge {
        display: inline-block;
        background: #fef3c7;
        color: #92400e;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .status-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📋 Job Application Tracker")  # main entry point for the Streamlit app

df = load_applications()  # load the underlying CSV/data store into a DataFrame

# ---------------------------------------------------------------------------
# Dashboard metrics summarising the current pipeline at a glance
# ---------------------------------------------------------------------------
st.markdown("---")
total = len(df)
active = len(df[~df["Status"].isin(["Rejected", "Ghosted"])]) if total else 0
moved_past_applied = len(df[df["Status"] != "Applied"]) if total else 0
response_rate = (moved_past_applied / total * 100) if total else 0

week_ago = datetime.now() - timedelta(days=7)
if total:
    apps_this_week = len(df[pd.to_datetime(df["Date Applied"]) >= week_ago])
else:
    apps_this_week = 0

    if active and total:
    active_df = df[~df["Status"].isin(["Rejected", "Ghosted"])].copy()
    active_df["_days"] = active_df["Date Applied"].apply(days_since_applied)
    avg_days = round(active_df["_days"].mean(), 1)
else:
    avg_days = 0

cols = st.columns(5)
metrics = [
    ("Total Applications", str(total)),
    ("Active", str(active)),
    ("Response Rate", f"{response_rate:.0f}%"),  # proportion of applications that moved past "Applied"
    ("This Week", str(apps_this_week)),
    ("Avg Days (Active)", str(avg_days)),
]
for col, (label, value) in zip(cols, metrics):
    col.markdown(
        f'<div class="metric-card"><h3>{label}</h3><p>{value}</p></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Add new application
# Uses a form so that submission is explicit and easy to validate before saving
# ---------------------------------------------------------------------------
with st.expander("➕ Log New Application", expanded=not total):
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        company = c1.text_input("Company Name *")
        role = c2.text_input("Role Title *")

        c3, c4, c5 = st.columns(3)
        date_applied = c3.date_input("Date Applied", value=date.today())
        source = c4.selectbox("Source", SOURCES)
        status = c5.selectbox("Status", STATUSES)

        c6, c7 = st.columns(2)
        contact_name = c6.text_input("Contact Name")
        contact_linkedin = c7.text_input("Contact LinkedIn URL")
        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Application", type="primary", use_container_width=True)
        if submitted:
            if not company or not role:
                st.error("Company name and role title are required.")
            else:
                df = add_application(
                    company, role, date_applied, source, status, notes, contact_name, contact_linkedin
                )
                st.success(f"Added {role} at {company}!")
                st.rerun()

# ---------------------------------------------------------------------------
# Update existing application
# Uses labels derived from the row to keep the index aligned with the underlying DataFrame
# ---------------------------------------------------------------------------
if total:
    with st.expander("✏️ Update Existing Application"):
        labels = [f"{r['Company']} — {r['Role']} ({r['Status']})" for _, r in df.iterrows()]
        selected_label = st.selectbox("Select an application", labels)
        selected_idx = labels.index(selected_label)
        row = df.iloc[selected_idx]

        with st.form("update_form"):
            new_status = st.selectbox("Status", STATUSES, index=STATUSES.index(row["Status"]))
            new_notes = st.text_area("Notes", value=row["Notes"] if pd.notna(row["Notes"]) else "")
            new_contact = st.text_input(
                "Contact Name", value=row["Contact Name"] if pd.notna(row["Contact Name"]) else ""
            )
            new_linkedin = st.text_input(
                "Contact LinkedIn URL",
                value=row["Contact LinkedIn"] if pd.notna(row["Contact LinkedIn"]) else "",
            )
            update_btn = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
            if update_btn:
                df = update_application(
                    selected_idx,
                    {
                        "Status": new_status,
                        "Notes": new_notes,
                        "Contact Name": new_contact,
                        "Contact LinkedIn": new_linkedin,
                    },
                )
                st.success("Application updated!")
                st.rerun()
       
        # AI outreach helper
        # This section uses the selected row to generate a suggested message, but never sends it anywhere.
        st.markdown("### AI Outreach Helper")
        st.write(
            "Click the button below to generate a suggested outreach message for the selected application."
        )

        if st.button("Generate outreach message"):
            contact_name = row["Contact Name"] if pd.notna(row["Contact Name"]) else ""
            contact_linkedin = row["Contact LinkedIn"] if pd.notna(row["Contact LinkedIn"]) else ""

            application_data = {
                "Company": row["Company"],
                "Role": row["Role"],
                "Contact Name": contact_name,
                "Contact LinkedIn": contact_linkedin,
                "Source": row["Source"],
                "Status": row["Status"],
                "Notes": row["Notes"],
                "Date Applied": row["Date Applied"],
            }

            with st.spinner("Generating..."):  # give feedback while waiting for the OpenAI API call
                try:
                    message = generate_outreach_message(application_data)  # note: function currently ignores most fields
                    st.markdown("**Suggested Outreach Message:**")
                    st.text_area("You can copy and tweak this:", message, height = 200)
                except Exception as e:
                    st.error(f"Could not generate message:  {e}")
# ---------------------------------------------------------------------------
# Application table with filters
# Everything below is read-only; it does not mutate the underlying CSV
# ---------------------------------------------------------------------------
if total:
    st.subheader("Applications")

    f1, f2, f3 = st.columns([1, 1, 2])
    status_filter = f1.multiselect("Filter by Status", STATUSES, default=[])
    sort_order = f2.selectbox("Sort by Date", ["Newest First", "Oldest First"])
    search = f3.text_input("Search by Company", "")

    view = df.copy()

    if status_filter:
        view = view[view["Status"].isin(status_filter)]
    if search:
        view = view[view["Company"].str.contains(search, case=False, na=False)]

    view["Date Applied"] = pd.to_datetime(view["Date Applied"])
    ascending = sort_order == "Oldest First"
    view = view.sort_values("Date Applied", ascending=ascending).reset_index(drop=True)

    view["Days Since Applied"] = view["Date Applied"].apply(days_since_applied)  # recomputed to reflect current date
    view["Follow-Up?"] = view.apply(needs_follow_up, axis=1).map({True: "⚠️ Needs follow-up", False: ""})

    def colour_status(val):
        bg = STATUS_COLOURS.get(val, "#e2e8f0")
        return f"background-color: {bg}; color: white; border-radius: 6px; padding: 2px 8px; font-weight: 600;"

    display_cols = [
        "Company",
        "Role",
        "Date Applied",
        "Source",
        "Status",
        "Days Since Applied",
        "Follow-Up?",
        "Notes",
        "Contact Name",
        "Contact LinkedIn",
    ]

    # Use pandas Styler to colour the status column and keep dates nicely formatted
    styled = (
        view[display_cols]
        .style.map(colour_status, subset=["Status"])
        .format({"Date Applied": lambda x: x.strftime("%Y-%m-%d") if pd.notna(x) else ""})
    )

    st.dataframe(
        styled,
        use_container_width=True,
        height=min(len(view) * 40 + 60, 600),
    )

    # Status breakdown
    st.subheader("Status Breakdown")
    status_counts = df["Status"].value_counts()
    chart_df = pd.DataFrame({"Status": status_counts.index, "Count": status_counts.values})
    st.bar_chart(chart_df, x="Status", y="Count", color="#3b82f6")
else:
    st.info("No applications yet. Use the form above to log your first one!")
