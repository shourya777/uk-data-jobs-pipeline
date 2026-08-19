



select
    posting_id,
    job_title,
    company_name,
    location_display,
    salary_min,
    salary_max,
    apply_url,
    posted_at
from "warehouse"."staging"."stg_job_postings"
