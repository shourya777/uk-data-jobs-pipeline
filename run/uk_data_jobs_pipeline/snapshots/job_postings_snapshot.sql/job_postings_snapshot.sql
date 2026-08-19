
      
    

    create  table
      "warehouse"."snapshots"."job_postings_snapshot"
  
    
    as (
      
    

    select *,
        md5(coalesce(cast(posting_id as varchar ), '')
         || '|' || coalesce(cast(now()::timestamp as varchar ), '')
        ) as dbt_scd_id,
        now()::timestamp as dbt_updated_at,
        now()::timestamp as dbt_valid_from,
        
  
  coalesce(nullif(now()::timestamp, now()::timestamp), null)
  as dbt_valid_to
from (
        



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

    ) sbq



    );
    
  
  