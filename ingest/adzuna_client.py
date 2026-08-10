"""
Adzuna Jobs API client — pulls UK data/analytics job postings.

Free developer tier: https://developer.adzuna.com/
Sign up, confirm your email, grab your `app_id` and `app_key` from the
dashboard, then set them as environment variables:

    export ADZUNA_APP_ID=...
    export ADZUNA_APP_KEY=...

Endpoint reference: https://developer.adzuna.com/docs/search

LEARNING TODOs (this is the part you should implement yourself):
  1. Pagination — `fetch_postings` below only pulls page 1. Adzuna returns
     `count` (total results) in the response body; loop pages until you've
     collected them all or hit a sane cap (e.g. 500 results).
  2. Retries — wrap the request in `tenacity.retry` (already in
     requirements.txt) so a transient 5xx/timeout doesn't kill the whole
     daily run.
  3. Idempotency — when you land this into DuckDB, upsert on Adzuna's `id`
     field rather than blindly appending, so re-running the script twice in
     a day doesn't create duplicate rows.
  4. Rate limiting — free tier is capped (check current limits on the
     developer dashboard); add a small `time.sleep()` between paginated
     requests to stay well under it.
"""

import os
import requests
import time
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path

ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs/gb/search"

# Analytics-engineer-adjacent titles worth pulling. Keep this list tight —
# Adzuna's `what` param does a keyword search, not an exact title match, so
# overly broad terms (e.g. just "data") pull in a lot of noise.
SEARCH_TERMS = [
    "analytics engineer",
    "data engineer",
    "data analyst",
    "data scientist",
    "business intelligence",
]

DEFAULT_LOCATION = "London"


def fetch_postings(search_term: str, location: str = DEFAULT_LOCATION, page: int = 1, results_per_page: int = 50) -> dict:

    app_id = os.environ.get("ADZUNA_APP_ID")
    app_key = os.environ.get("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        raise RuntimeError(
            "Set ADZUNA_APP_ID and ADZUNA_APP_KEY environment variables. "
            "Sign up for free at https://developer.adzuna.com/"
        )

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": search_term,
        "where": location,
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }
    resp = requests.get(f"{ADZUNA_BASE_URL}/{page}", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()

def fetch_all_postings(max_per_term: int = 5) -> list[dict]:
    """
    Pulls postings for every term in SEARCH_TERMS, paginating each one,
    and dedupes across terms by Adzuna's job `id`.
    """
    results_by_id = {}

    for term in SEARCH_TERMS:
        page = 1
        collected_for_term = 0

        while collected_for_term < max_per_term:
            data = fetch_postings(term, page=page)
            jobs = data.get("results", [])

            if not jobs:
                break 

            for job in jobs:
                results_by_id[job["id"]] = job

            collected_for_term += len(jobs)
            page += 1
            time.sleep(0.5)  

    return list(results_by_id.values())

def save_postings(jobs: list[dict]) -> str:
    """Writes fetched postings to data/raw/ as a timestamped JSON file."""
    out_dir = Path(__file__).parent.parent / "data" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out_path = out_dir / f"adzuna_{timestamp}.json"
    with open(out_path, "w") as f:
        json.dump(jobs, f, indent=2)
    return str(out_path)

if __name__ == "__main__":
    jobs = fetch_all_postings(max_per_term=5)
    print(f"Collected {len(jobs)} unique postings across {len(SEARCH_TERMS)} search terms")
    path = save_postings(jobs)
    print(f"Saved to {path}")