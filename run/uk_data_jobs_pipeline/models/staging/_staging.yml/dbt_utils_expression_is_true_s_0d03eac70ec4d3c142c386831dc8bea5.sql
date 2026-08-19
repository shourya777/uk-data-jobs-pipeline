
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  



select
    1
from (select * from "warehouse"."staging"."stg_job_postings" where salary_min is not null and salary_max is not null) dbt_subquery

where not(salary_min <= salary_max)


  
  
      
    ) dbt_internal_test