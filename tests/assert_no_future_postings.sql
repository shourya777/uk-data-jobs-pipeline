-- Singular test: a job posting can't have been posted in the future.
-- dbt convention — a singular test is just a SQL query that should return
-- ZERO rows when the data is valid. Any row returned = test failure.

select
    posting_id,
    posted_at
from {{ ref('stg_job_postings') }}
where posted_at > current_timestamp
