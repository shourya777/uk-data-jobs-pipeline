"""
Streamlit dashboard reading directly from the DuckDB marts. Run locally
with:

    streamlit run dashboard/app.py

Skills-in-demand chart is intentionally left as a TODO: it depends on
bridge_posting_skill.sql, which is still an unimplemented stub (deferred
stretch goal, same as fuzzy_match_sponsor).
"""

from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
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

st.subheader("Postings over time")
postings_over_time = con.execute(
    """
    select date_day, count(distinct posting_id) as open_postings
    from marts.fct_job_postings
    group by 1
    order by 1
    """
).df()
if postings_over_time.empty:
    st.info("No data yet — run the ingestion + dbt pipeline first.")
else:
    st.line_chart(postings_over_time.set_index("date_day"))

st.subheader("Top hiring companies")
category_options = ["All"] + [
    row[0]
    for row in con.execute(
        "select distinct sponsor_category from marts.dim_company order by 1"
    ).fetchall()
]
selected_category = st.selectbox("Filter by sponsor category", category_options)

query = """
    select dc.company_name, count(distinct f.posting_id) as posting_count
    from marts.fct_job_postings f
    join marts.dim_company dc on f.company_key = dc.company_key
"""
params = []
if selected_category != "All":
    query += " where dc.sponsor_category = ?"
    params.append(selected_category)
query += " group by 1 order by posting_count desc limit 15"

top_companies = con.execute(query, params).df()
if top_companies.empty:
    st.info("No companies match this filter yet.")
else:
    st.bar_chart(top_companies.set_index("company_name"))

st.subheader("Skills in demand")
st.info(
    "Blocked on models/marts/bridge_posting_skill.sql, which is still an "
    "unimplemented stub. Once that model exists: join fct_job_postings to "
    "bridge_posting_skill to dim_skill, count(distinct posting_id) per "
    "skill_name, st.bar_chart(...)."
)

st.subheader("Salary distribution by category")
salary_df = con.execute(
    """
    select sponsor_category, salary_min, salary_max
    from marts.fct_job_postings
    where salary_min is not null and salary_max is not null
    """
).df()
if salary_df.empty:
    st.info("No salary data available yet (Adzuna doesn't report salary on every posting).")
else:
    salary_df["salary_mid"] = (salary_df["salary_min"] + salary_df["salary_max"]) / 2
    fig = px.box(
        salary_df,
        x="sponsor_category",
        y="salary_mid",
        points="all",
        labels={"salary_mid": "Estimated salary (midpoint, GBP)", "sponsor_category": "Sponsor category"},
    )
    st.plotly_chart(fig, use_container_width=True)