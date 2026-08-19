with postings as (

    select distinct
        company_name,
        sponsor_entity,
        category,
        is_verified_sponsor
    from "warehouse"."intermediate"."int_postings_sponsor_matched"

)

select
    md5(cast(coalesce(cast(company_name as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as company_key,
    company_name,
    sponsor_entity,
    coalesce(category, 'Unverified') as sponsor_category,
    is_verified_sponsor
from postings