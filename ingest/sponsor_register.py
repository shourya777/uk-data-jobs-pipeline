"""
UK Home Office "Register of licensed sponsors: workers" loader.

This is a public, free, no-auth CSV published by gov.uk and updated
regularly (roughly weekly). It's the authoritative list of organisations
licensed to sponsor Skilled Worker / Global Business Mobility visas —
much more reliable than any "mentions sponsorship" text classifier.

Source page (find the current dated CSV link on this page — it changes
filename each publish, e.g. ..._Register_-_2026-07-22.csv):
    https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers
"""

import re
from pathlib import Path

import requests

REGISTER_PAGE_URL = "https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers"
CSV_URL_PATTERN = re.compile(
    r"https://assets\.publishing\.service\.gov\.uk/media/[^\s\"]+?Worker_and_Temporary_Worker_Web_Register[^\s\"]+?\.csv"
)


def find_latest_csv_url() -> str:
    """
    Fetches the gov.uk publications page and regex-matches the current
    dated CSV asset link out of the raw HTML.
    """
    resp = requests.get(REGISTER_PAGE_URL, timeout=30)
    resp.raise_for_status()
    match = CSV_URL_PATTERN.search(resp.text)
    if not match:
        raise RuntimeError(
            "Couldn't find a sponsor register CSV link on the gov.uk page. "
            "The page structure may have changed — check "
            f"{REGISTER_PAGE_URL} manually and update CSV_URL_PATTERN."
        )
    return match.group(0)


def download_register(dest_path: str) -> str:
    """
    Finds the current CSV URL and streams it to dest_path.
    """
    url = find_latest_csv_url()
    dest = Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
    return str(dest)


if __name__ == "__main__":
    from datetime import datetime, timezone

    url = find_latest_csv_url()
    print(f"Found register CSV: {url}")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out_path = Path(__file__).parent.parent / "data" / "raw" / f"uk_sponsors_{timestamp}.csv"
    path = download_register(str(out_path))
    print(f"Saved to {path}")