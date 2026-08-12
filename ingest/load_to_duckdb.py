"""
Loads raw JSON (Adzuna) and CSV (sponsor register) files from data/raw/
into DuckDB tables `raw_job_postings` and `raw_sponsor_register`.

This is the "L" in a small EL(T) pipeline — dbt takes over from here for
the "T". Keep business logic OUT of this script; it should only reshape
JSON into tabular rows and load, nothing more.
"""

import glob
import json
from pathlib import Path

import duckdb

DB_PATH = Path(__file__).parent.parent / "data" / "warehouse.duckdb"
RAW_DIR = Path(__file__).parent.parent / "data" / "raw"

RAW_JOB_POSTINGS_SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_job_postings (
    id VARCHAR PRIMARY KEY,
    title VARCHAR,
    company_name VARCHAR,
    location_display VARCHAR,
    salary_min DOUBLE,
    salary_max DOUBLE,
    description VARCHAR,
    created_at TIMESTAMP,
    redirect_url VARCHAR,
    search_term VARCHAR,
    loaded_at TIMESTAMP DEFAULT current_timestamp
);
"""

RAW_SPONSOR_REGISTER_SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_sponsor_register (
    organisation_name VARCHAR,
    town_city VARCHAR,
    county VARCHAR,
    type_and_rating VARCHAR,
    route VARCHAR,
    loaded_at TIMESTAMP DEFAULT current_timestamp
);
"""


def get_connection() -> duckdb.DuckDBPyConnection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def load_job_postings(con: duckdb.DuckDBPyConnection) -> int:
    """
    Reads the most recent data/raw/adzuna_*.json dump, flattens the nested
    Adzuna response into flat columns, and upserts into raw_job_postings
    keyed on `id`. Only the latest file is loaded (not every historical
    dump) — raw_job_postings represents current state; the dbt snapshot
    downstream is what gives you history, so re-loading old files here
    would be redundant.
    """
    con.execute(RAW_JOB_POSTINGS_SCHEMA)

    files = sorted(RAW_DIR.glob("adzuna_*.json"))
    if not files:
        raise FileNotFoundError(
            f"No adzuna_*.json files found in {RAW_DIR}. Run "
            "`python -m ingest.adzuna_client` first."
        )
    latest_file = files[-1]  # timestamped filenames sort chronologically

    with open(latest_file) as f:
        jobs = json.load(f)

    rows = []
    for job in jobs:
        created_raw = job.get("created")
        # Adzuna returns "...Z" (Zulu/UTC) suffixes, which DuckDB's
        # timestamp parser is happier receiving as an explicit UTC offset.
        created_at = created_raw.replace("Z", "+00:00") if created_raw else None

        rows.append((
            job["id"],
            job.get("title"),
            job.get("company", {}).get("display_name"),
            job.get("location", {}).get("display_name"),
            job.get("salary_min"),
            job.get("salary_max"),
            job.get("description"),
            created_at,
            job.get("redirect_url"),
            job.get("_search_term"),
        ))

    con.executemany(
        """
        INSERT OR REPLACE INTO raw_job_postings
            (id, title, company_name, location_display, salary_min, salary_max,
             description, created_at, redirect_url, search_term)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    return len(rows)


def load_sponsor_register(con: duckdb.DuckDBPyConnection) -> int:
    """
    Reads the most recent data/raw/uk_sponsors_*.csv via DuckDB's native
    read_csv_auto (fast — no need to round-trip through pandas), renames
    the government's human-formatted headers to snake_case, and replaces
    the full raw_sponsor_register table each run. Full replace (not
    upsert) is deliberate: the register is a complete list each time it's
    published, not an incremental diff, so "replace everything with the
    latest download" is the correct semantics here.
    """
    con.execute(RAW_SPONSOR_REGISTER_SCHEMA)

    files = sorted(RAW_DIR.glob("uk_sponsors_*.csv"))
    if not files:
        raise FileNotFoundError(
            f"No uk_sponsors_*.csv files found in {RAW_DIR}. Run "
            "`python -m ingest.sponsor_register` first."
        )
    latest_file = files[-1]

    con.execute("DELETE FROM raw_sponsor_register")
    con.execute(
        """
        INSERT INTO raw_sponsor_register
            (organisation_name, town_city, county, type_and_rating, route)
        SELECT
            "Organisation Name" AS organisation_name,
            "Town/City"         AS town_city,
            "County"            AS county,
            "Type & Rating"     AS type_and_rating,
            "Route"             AS route
        FROM read_csv_auto(?, header=True)
        """,
        [str(latest_file)],
    )
    return con.execute("SELECT count(*) FROM raw_sponsor_register").fetchone()[0]


if __name__ == "__main__":
    con = get_connection()
    n_postings = load_job_postings(con)
    n_sponsors = load_sponsor_register(con)
    print(f"Loaded {n_postings} job postings, {n_sponsors} sponsor register rows into {DB_PATH}")
    con.close()