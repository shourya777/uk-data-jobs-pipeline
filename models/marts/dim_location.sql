with postings as (

    select distinct location_display
    from {{ ref('int_postings_sponsor_matched') }}

)

select
    {{ dbt_utils.generate_surrogate_key(['location_display']) }} as location_key,
    location_display,
    -- TODO (learning exercise): split location_display (e.g. "Camden,
    -- London, UK") into city / region / country columns. Adzuna's raw
    -- response actually gives you a `location.area` array with this
    -- already broken out — consider capturing that in stg_job_postings
    -- instead of re-parsing a display string here.
    location_display as city_raw
from postings
