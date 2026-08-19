






    with grouped_expression as (
    select
        
        
    
  
( 1=1 and salary_min >= 0 and salary_min <= 500000
)
 as expression


    from "warehouse"."marts"."fct_job_postings"
    where
        salary_min is not null
    
    

),
validation_errors as (

    select
        *
    from
        grouped_expression
    where
        not(expression = true)

)

select *
from validation_errors







