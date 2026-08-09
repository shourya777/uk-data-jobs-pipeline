# Project Plan — UK Data & Analytics Jobs Pipeline

A learning roadmap and architecture reference for building this project end to end. Follow the phases in order — each one produces something demoable, so you can commit and push after every phase rather than disappearing for three weeks and shipping once.

## 1. The pitch (what this project proves)

A daily-refreshed analytics pipeline that answers a real question — *"which companies are actually hiring for data/analytics roles in the UK right now, and are they genuinely licensed to sponsor a visa?"* — using the modern data stack employers ask for in analytics engineer job specs: SQL, dbt, a cloud-style warehouse, orchestration, CI/CD, data modeling, testing, and a semantic/BI layer.

It's not a toy dataset (Iris, Titanic, jaffle-shop). It ingests two real, live, freely-available sources:

1. **Adzuna Jobs API** (free developer tier) — live UK job postings for analytics/data roles.
2. **UK Home Office "Register of Licensed Sponsors: Workers"** — the actual government CSV of companies licensed to sponsor Skilled Worker visas.

Nobody else's portfolio has this exact combination, which matters — recruiters have seen a hundred jaffle-shop forks.

## 2. Architecture at a glance

```
Adzuna API ─┐
            ├─► raw landing (DuckDB, /data/raw) ─► dbt staging ─► dbt intermediate ─► dbt marts ─► Streamlit dashboard
UK Sponsor  ─┘         ▲                                │
Register CSV            │                          dbt snapshots (SCD2 history of each posting)
                         │
                 GitHub Actions (daily cron) orchestrates ingestion + dbt build + docs deploy
                 GitHub Actions (on PR) runs dbt build/test against fixture data — CI gate
```

Why DuckDB instead of Snowflake/BigQuery: it's free, runs in GitHub Actions with zero infrastructure, and the whole thing is reproducible by a recruiter with `git clone && dbt build` — no cloud account required. The `profiles.yml` is written so swapping the `duckdb` target for a `snowflake` or `bigquery` target is a config change, not a rewrite — mention this explicitly in your README, it signals you understand the stack is warehouse-agnostic.

## 3. Data model (star schema)

- **`fct_job_postings`** (grain: one row per posting per day it was seen active, from the snapshot) — foreign keys to all dims, plus `salary_min`, `salary_max`, `is_verified_sponsor`.
- **`dim_company`** — company name, sponsor entity name (from the register), sponsor category (Direct Employer / Consulting / Public Sector), first-seen date.
- **`dim_location`** — city, region, lat/long if available.
- **`dim_date`** — standard date dimension (day, week, month, is_weekend, etc.) — generate with a dbt package (`dbt_date` or `dbt-labs/dbt-utils`), don't hand-write it.
- **`dim_skill`** + **`bridge_posting_skill`** — many-to-many: one posting mentions many skills (SQL, Python, dbt, Airflow, Snowflake...), extracted from the job description with simple regex/keyword matching in a Python step or a dbt macro. This bridge table is what makes the "skills in demand" chart possible and is a nice talking point in interviews — it's a lightweight NLP-adjacent feature.

Use `dbt snapshots` on the raw postings table (keyed by Adzuna's job id) to get SCD Type 2 for free — this is exactly the kind of "implement SCD2" requirement that shows up in analytics engineer job specs, and dbt gives you a one-file implementation instead of hand-rolled merge logic.

## 4. Build phases

**Phase 0 — Setup (this repo does this for you)**
Repo scaffold, dbt project skeleton, sample fixture data so `dbt build` works immediately without any API keys.

**Phase 1 — Ingestion (you write this)**
Finish `ingest/adzuna_client.py` and `ingest/sponsor_register.py` (stubs are provided with docstrings and the exact endpoints/CSV URL). Land raw JSON/CSV into `data/raw/` and load into DuckDB tables `raw_job_postings` and `raw_sponsor_register`. This is where you practice: API pagination, rate limiting/retries, idempotent loads (don't duplicate rows on re-run).

**Phase 2 — Staging models**
One `stg_` model per raw source. Rename columns to consistent snake_case, cast types, do zero business logic here — this is the dbt convention and interviewers will ask why you separate staging from marts.

**Phase 3 — Snapshots**
Wire up the dbt snapshot on `stg_job_postings`. Run it daily (via the GitHub Action) and watch history accumulate — after a week you'll have real "how long does a posting stay open" data.

**Phase 4 — Intermediate + sponsor matching**
`int_postings_sponsor_matched.sql` joins postings to the sponsor register. Reuse the matching logic and false-positive lessons documented in `docs/sponsor_matching_notes.md` (included) — this file alone is a good interview talking point: "here's how I avoided false-positive company matches."

**Phase 5 — Marts + tests**
Build the star schema. Add schema tests (`not_null`, `unique`, `relationships`, `accepted_values`) plus at least one custom singular test (e.g. `salary_min <= salary_max`). Add `dbt source freshness` checks on the raw sources since this is a daily-refreshed pipeline — freshness tests are underused in portfolios and specifically called out in job specs.

**Phase 6 — Semantic layer (stretch goal)**
Define 2-3 metrics with dbt's MetricFlow (`postings_count`, `median_salary`, `sponsor_rate`) in a `models/marts/_metrics.yml`. This is a newer, actively-hiring-for skill — even a minimal implementation stands out.

**Phase 7 — CI/CD**
`.github/workflows/ci.yml` (provided, working) runs `dbt build` + `dbt test` against the seed fixtures on every PR — this is your CI gate. `.github/workflows/daily_refresh.yml` (provided, working structure, needs your `ADZUNA_APP_ID`/`ADZUNA_APP_KEY` repo secrets) runs the real daily ingestion + dbt run + publishes `dbt docs` to GitHub Pages.

**Phase 8 — Dashboard**
`dashboard/app.py` is a Streamlit skeleton reading directly from the DuckDB marts. Build 3-4 charts: postings over time, top hiring companies, skills in demand, salary distribution by category. Deploy free on Streamlit Community Cloud and link it from your README — a live link recruiters can click matters more than screenshots.

**Phase 9 — Polish for recruiters**
Finish the README (structure provided), add a real architecture diagram (mermaid, provided as a starting point), write 2-3 short "engineering decisions" notes (why DuckDB, why dbt snapshots, why Adzuna over scraping) — this "roadblocks and tradeoffs" framing is explicitly what hiring managers say they look for in a portfolio repo.

## 5. Suggested CV / LinkedIn bullet points (fill in once built)

- Built an end-to-end analytics engineering pipeline (Python → DuckDB → dbt → Streamlit) ingesting live UK job market data daily via GitHub Actions, modeling 1,000+ postings into a dimensional star schema with SCD2 history via dbt snapshots.
- Cross-referenced job postings against the UK Home Office's official sponsor licence register to flag verified visa-sponsoring employers, replacing an unreliable ML-classifier signal with a deterministic, auditable match.
- Implemented a full CI/CD pipeline (GitHub Actions) running dbt build/test on every pull request against fixture data, plus a scheduled production refresh with automated dbt docs publishing.
- Defined a semantic layer (dbt MetricFlow) exposing standardized metrics (posting volume, median salary, sponsor rate) for consistent reporting across a Streamlit dashboard.

## 6. Learning resources by skill

- **dbt fundamentals**: dbt Labs' free "dbt Fundamentals" course (getdbt.com/learn).
- **Data modeling / star schema**: Ralph Kimball's dimensional modeling primer (search "Kimball dimensional modeling cheat sheet").
- **dbt snapshots**: docs.getdbt.com/docs/build/snapshots.
- **dbt tests**: docs.getdbt.com/docs/build/data-tests + the `dbt-labs/dbt-utils` and `calogica/dbt-expectations` packages for richer tests.
- **MetricFlow / semantic layer**: docs.getdbt.com/docs/build/build-metrics-intro.
- **GitHub Actions for data**: search "GitHub Actions dbt CI cron schedule example" for reference workflows.
- **SQL practice**: window functions and CTEs specifically, since that's what job specs call out — SQLZoo or Advent of SQL for drills.

## 7. Scope discipline

Don't gold-plate. A working Phase 0-5 with a clean README and one deployed dashboard is a stronger portfolio piece than an ambitious Phase 0-9 that's half-broken. Ship Phase 5, write the README, put it on GitHub, then keep iterating in public — commit history showing incremental progress is itself a signal recruiters read positively.
