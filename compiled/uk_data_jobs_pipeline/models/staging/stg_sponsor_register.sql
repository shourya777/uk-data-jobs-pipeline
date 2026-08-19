-- Mirrors the pattern in stg_job_postings.sql: fall back to the seed in
-- CI (no live ingestion runs there), select from the real source otherwise.
-- Note: the CI seed preserves the government's original CSV headers
-- ("Organisation Name" etc.) since it was captured verbatim from the real
-- register for realism — so unlike stg_job_postings, this branch needs an
-- explicit rename to snake_case before the two branches line up.


    with source as (
        select * from "warehouse"."main"."raw_sponsor_register"
    )


, renamed as (

    select
        trim(organisation_name)                                as organisation_name,
        trim(town_city)                                         as town_city,
        trim(county)                                            as county,
        trim(type_and_rating)                                   as type_and_rating,
        trim(route)                                             as route,
        type_and_rating ilike '%A rating%'                      as is_a_rated,
        current_timestamp                                       as _loaded_at

    from source
    where organisation_name is not null

)

select * from renamed