
  
  create view "warehouse"."staging"."stg_job_postings__dbt_tmp" as (
    -- Worked example: this is the one staging model built all the way
-- through, so you have a concrete pattern to copy for the others.
--
-- Pattern: in the `ci` target (see profiles.yml.example) there's no live
-- `raw_job_postings` table, because CI never runs the real ingestion
-- scripts against the Adzuna API. Instead we fall back to the
-- `sample_job_postings` seed, which was captured from real (verified)
-- postings so tests run against realistic data. In `dev`/`prod` targets,
-- this selects from the actual source once you've implemented
-- ingest/load_to_duckdb.py.
--
-- This is a reasonable pattern for any portfolio project where the "real"
-- data source needs paid/rate-limited API credentials: keep CI honest and
-- reproducible with a frozen fixture, keep prod live.


    with source as (
        select * from "warehouse"."main"."raw_job_postings"
    )


, renamed as (

    select
        id                                          as posting_id,
        trim(title)                                 as job_title,
        trim(company_name)                          as company_name,
        trim(location_display)                      as location_display,
        try_cast(salary_min as double)               as salary_min,
        try_cast(salary_max as double)               as salary_max,
        description,
        cast(created_at as timestamp)                as posted_at,
        redirect_url                                as apply_url,
        search_term,
        current_timestamp                            as _loaded_at

    from source
    where title is not null
      and company_name is not null

)

select * from renamed
  );
