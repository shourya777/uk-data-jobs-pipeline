"""
Loads raw JSON (Adzuna) and CSV (sponsor register) files from data/raw/
into DuckDB tables `raw_job_postings` and `raw_sponsor_register`.

This is the "L" in a small EL(T) pipeline — dbt takes over from here for
the "T". Keep business logic OUT of this script; it should only reshape
JSON into tabular rows and load, nothing more.

LEARNING TODOs:
  1. `load_job_postings()` — read every data/raw/adzuna_*.json file,
     flatten the nested Adzuna response (company.display_name,
     location.display_name, etc. need to become flat columns), and
     INSERT OR REPLACE into raw_job_postings keyed on `id` so repeat runs
     are idempotent.
  2. `load_sponsor_register()` — read the latest data/raw/uk_sponsors_*.csv
     via DuckDB's native `read_csv_auto`, load into raw_sponsor_register.
  3. Consider: should raw_job_postings be append-only (new table per day)
     or upserted in place? This project uses upsert-in-place for the raw
     table + a dbt snapshot downstream for history — that split (raw =
     current state, snapshot = history) is a deliberate design choice
     worth explaining in your README.
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
    TODO: implement per the module docstring. Return the number of rows
    loaded so the calling script (and the GitHub Action log) can report it.
    """
    con.execute(RAW_JOB_POSTINGS_SCHEMA)
    raise NotImplementedError("Read data/raw/adzuna_*.json, flatten, upsert into raw_job_postings.")


def load_sponsor_register(con: duckdb.DuckDBPyConnection) -> int:
    """TODO: implement per the module docstring."""
    con.execute(RAW_SPONSOR_REGISTER_SCHEMA)
    raise NotImplementedError("Read the latest data/raw/uk_sponsors_*.csv into raw_sponsor_register.")


if __name__ == "__main__":
    con = get_connection()
    n_postings = load_job_postings(con)
    n_sponsors = load_sponsor_register(con)
    print(f"Loaded {n_postings} job postings, {n_sponsors} sponsor register rows into {DB_PATH}")
    con.close()
