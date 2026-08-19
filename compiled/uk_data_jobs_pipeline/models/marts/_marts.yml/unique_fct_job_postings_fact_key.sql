
    
    

select
    fact_key as unique_field,
    count(*) as n_records

from "warehouse"."marts"."fct_job_postings"
where fact_key is not null
group by fact_key
having count(*) > 1


