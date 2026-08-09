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
    """
    Fetch one page of results for a single search term.

    Returns the raw parsed JSON response. See the Adzuna docs for the full
    response schema — the fields you'll care about most for this project are:
    id, title, company.display_name, location.display_name, description,
    salary_min, salary_max, created (posting date), redirect_url (apply link).
    """
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


def fetch_all_postings() -> list[dict]:
    """
    TODO (learning exercise): loop over SEARCH_TERMS and paginate through
    each one using fetch_postings(), dedupe by Adzuna `id` (the same job
    can surface under multiple search terms), and return a flat list of
    posting dicts ready to write to data/raw/.

    A minimal correct implementation is ~20 lines. Resist the urge to
    over-engineer this on day one — get one search term, one page, working
    end to end into DuckDB first, then come back and expand it.
    """
    raise NotImplementedError("Implement pagination + dedupe here — see the docstring.")


if __name__ == "__main__":
    # Smoke test: pull page 1 for the first search term and print a summary.
    data = fetch_postings(SEARCH_TERMS[0])
    print(f"Total results reported by Adzuna: {data.get('count')}")
    for job in data.get("results", [])[:5]:
        print(f"- {job['title']} @ {job['company']['display_name']} ({job['location']['display_name']})")
