



select
    1
from (select * from "warehouse"."staging"."stg_job_postings" where salary_min is not null and salary_max is not null) dbt_subquery

where not(salary_min <= salary_max)

