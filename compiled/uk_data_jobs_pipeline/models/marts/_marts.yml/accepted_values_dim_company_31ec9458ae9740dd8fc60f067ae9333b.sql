
    
    

with all_values as (

    select
        sponsor_category as value_field,
        count(*) as n_records

    from "warehouse"."marts"."dim_company"
    group by sponsor_category

)

select *
from all_values
where value_field not in (
    'Direct Employer','Consulting','IT Consulting','Public Sector','Unverified'
)


