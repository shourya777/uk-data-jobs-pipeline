
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select posting_id
from "warehouse"."staging"."stg_job_postings"
where posting_id is null



  
  
      
    ) dbt_internal_test