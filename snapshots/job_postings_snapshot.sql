{#
  SCD Type 2 history of every posting, keyed on posting_id. Every time this
  snapshot runs (daily, via the GitHub Action) dbt compares the current
  state of stg_job_postings against the snapshot table and:
    - inserts new rows for postings we haven't seen before
    - closes out (sets dbt_valid_to) rows for postings that changed or
      disappeared (i.e. were filled/removed) since the last run
    - leaves unchanged postings alone

  This is what gives you "how long did this posting stay open" and
  "did the salary range change" for free, without hand-writing merge SQL.
  Read: https://docs.getdbt.com/docs/build/snapshots

  check_cols is deliberately narrow — job_title/salary can legitimately get
  edited by the poster; posting_id + company_name is the identity, the rest
  is what we track changes on.
#}

{% snapshot job_postings_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='posting_id',
        strategy='check',
        check_cols=['job_title', 'salary_min', 'salary_max', 'location_display'],
    )
}}

select
    posting_id,
    job_title,
    company_name,
    location_display,
    salary_min,
    salary_max,
    apply_url,
    posted_at
from {{ ref('stg_job_postings') }}

{% endsnapshot %}
