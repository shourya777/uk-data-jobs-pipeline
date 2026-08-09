"""
UK Home Office "Register of licensed sponsors: workers" loader.

This is a public, free, no-auth CSV published by gov.uk and updated
regularly (roughly weekly). It's the authoritative list of organisations
licensed to sponsor Skilled Worker / Global Business Mobility visas —
much more reliable than any "mentions sponsorship" text classifier.

Source page (find the current dated CSV link on this page — it changes
filename each publish, e.g. ..._Register_-_2026-07-22.csv):
    https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers

LEARNING TODOs:
  1. `find_latest_csv_url()` below is a stub — scrape the publications page
     for the current .csv asset link (a simple regex on the HTML for
     `assets.publishing.service.gov.uk/media/.../SP_-_Worker_and_Temporary
     _Worker_Web_Register_-_\\d{4}-\\d{2}-\\d{2}\\.csv` works fine, no need
     for a full HTML parser).
  2. `download_register()` — download to data/raw/uk_sponsors_<date>.csv.
     Keep the date in the filename; you'll want historical snapshots later
     if you extend the project to track *when* companies gain/lose their
     licence.
  3. Matching logic — see docs/sponsor_matching_notes.md for the hard-won
     lessons on why naive substring matching produces false positives
     (e.g. "Zego" incorrectly matching "Azego TS Ltd", "Sky" matching
     "Sky Supermarket" instead of "Sky UK Limited"). Don't skip that file.
"""

import re
import requests

REGISTER_PAGE_URL = "https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers"
CSV_URL_PATTERN = re.compile(
    r"https://assets\.publishing\.service\.gov\.uk/media/[^\s\"]+?Worker_and_Temporary_Worker_Web_Register[^\s\"]+?\.csv"
)


def find_latest_csv_url() -> str:
    """
    TODO: fetch REGISTER_PAGE_URL, run CSV_URL_PATTERN against the HTML,
    return the first match. Raise a clear error if nothing is found (the
    gov.uk page structure occasionally changes).
    """
    raise NotImplementedError("Implement the scrape + regex match here.")


def download_register(dest_path: str) -> str:
    """
    TODO: call find_latest_csv_url(), stream the CSV to dest_path, return
    the path. Use requests with stream=True for the (fairly large, ~10MB)
    download rather than loading it all into memory at once.
    """
    raise NotImplementedError("Implement the download here.")


if __name__ == "__main__":
    url = find_latest_csv_url()
    print(f"Found register CSV: {url}")
