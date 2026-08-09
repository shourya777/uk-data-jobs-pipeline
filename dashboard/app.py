"""
Streamlit dashboard reading directly from the DuckDB marts. Run locally
with:

    streamlit run dashboard/app.py

Deploy free at https://streamlit.io/cloud once it's working locally —
point it at this file, it'll pick up requirements.txt automatically.
Link the live URL from your README; a clickable dashboard beats a
screenshot every time.

LEARNING TODOs — build these out one at a time, commit after each:
  1. Postings over time (line chart) — count of fct_job_postings rows
     grouped by date_day.
  2. Top hiring companies (bar chart) — count of distinct posting_id
     grouped by company_name from dim_company, filterable by
     sponsor_category.
  3. Skills in demand (bar chart) — count from bridge_posting_skill
     joined to dim_skill, once that model is implemented.
  4. Salary distribution (box plot or histogram) — salary_min/salary_max
     from fct_job_postings, split by sponsor_category.

Keep queries simple — this dashboard should mostly be `SELECT ... FROM
marts.fct_... GROUP BY ...`, not a place to put business logic. If you
find yourself writing a complex CASE WHEN here, it probably belongs in a
dbt mart instead.
"""

from pathlib import Path

import duckdb
import streamlit as st

DB_PATH = Path(__file__).parent.parent / "data" / "warehouse.duckdb"

st.set_page_config(page_title="UK Data & Analytics Jobs", layout="wide")
st.title("UK Data & Analytics Jobs — Live Market Pipeline")
st.caption(
    "Daily-refreshed via Adzuna's API + the UK Home Office sponsor register. "
    "Source: github.com/YOUR_USERNAME/uk-data-jobs-pipeline"
)


@st.cache_resource
def get_connection():
    return duckdb.connect(str(DB_PATH), read_only=True)


if not DB_PATH.exists():
    st.warning(
        "No warehouse found yet. Run `dbt seed --target ci && dbt build --target ci` "
        "(or the full dev pipeline once ingestion is implemented) to generate "
        f"{DB_PATH}, then rerun this app."
    )
    st.stop()

con = get_connection()

col1, col2, col3 = st.columns(3)
with col1:
    total = con.execute("select count(distinct posting_id) from marts.fct_job_postings").fetchone()[0]
    st.metric("Postings tracked", total)
with col2:
    companies = con.execute("select count(distinct company_key) from marts.dim_company").fetchone()[0]
    st.metric("Companies", companies)
with col3:
    verified = con.execute(
        "select count(distinct company_key) from marts.dim_company where is_verified_sponsor"
    ).fetchone()[0]
    st.metric("Verified sponsors", verified)

st.divider()
st.subheader("TODO: postings over time")
st.info("Implement: SELECT date_day, count(distinct posting_id) FROM marts.fct_job_postings GROUP BY 1 ORDER BY 1, then st.line_chart(...).")

st.subheader("TODO: top hiring companies")
st.info("Implement: join fct_job_postings to dim_company, group by company_name, count distinct posting_id, st.bar_chart(...).")

st.subheader("TODO: skills in demand")
st.info("Implement once bridge_posting_skill exists: join to dim_skill, count postings per skill, st.bar_chart(...).")

st.subheader("TODO: salary distribution by category")
st.info("Implement: salary_min/salary_max from fct_job_postings grouped by sponsor_category, plotly box plot via st.plotly_chart(...).")
