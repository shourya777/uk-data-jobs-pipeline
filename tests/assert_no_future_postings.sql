-- Singular test: a job posting shouldn't be posted far in the future.
-- Downgraded to a warning rather than a hard failure: live job-board
-- feeds (Adzuna aggregates from many underlying ATSs) occasionally
-- surface listings with a scheduled/embargoed go-live timestamp slightly
-- ahead of the actual feed-scrape time. A handful of postings a few
-- hours in the future is expected noise in real data, not a pipeline
-- bug — but if this count grows large or postings show up dated months
-- or years ahead, that's a genuine signal something's broken upstream
-- (e.g. a timezone parsing bug), worth investigating.

{{ config(severity = 'warn') }}

select
    posting_id,
    posted_at
from {{ ref('stg_job_postings') }}
where posted_at > current_timestamp