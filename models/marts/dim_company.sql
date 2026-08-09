with postings as (

    select distinct
        company_name,
        sponsor_entity,
        category,
        is_verified_sponsor
    from {{ ref('int_postings_sponsor_matched') }}

)

select
    {{ dbt_utils.generate_surrogate_key(['company_name']) }} as company_key,
    company_name,
    sponsor_entity,
    coalesce(category, 'Unverified') as sponsor_category,
    is_verified_sponsor
from postings
