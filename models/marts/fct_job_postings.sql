-- Grain: one row per posting_id per day it was observed active, sourced
-- from the SCD2 snapshot (so a posting open for 10 days produces 10 rows
-- here — that's deliberate, it's what makes "postings over time" and
-- "days active" charts possible downstream).
--
-- dbt_valid_to is null for rows still current; we generate one row per
-- calendar day between dbt_valid_from and coalesce(dbt_valid_to, today)
-- using dbt_utils.date_spine, then join back to the sponsor match +
-- dimension keys.

with snapshot as (

    select * from {{ ref('job_postings_snapshot') }}

),

sponsor_matched as (

    select posting_id, sponsor_entity, category, is_verified_sponsor
    from {{ ref('int_postings_sponsor_matched') }}

),

date_spine as (

    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2026-01-01' as date)",
        end_date="cast('2027-12-31' as date)"
    ) }}

),

active_days as (

    select
        snapshot.posting_id,
        snapshot.company_name,
        snapshot.job_title,
        snapshot.location_display,
        snapshot.salary_min,
        snapshot.salary_max,
        snapshot.apply_url,
        date_spine.date_day as observed_date
    from snapshot
    inner join date_spine
        on date_spine.date_day >= cast(snapshot.dbt_valid_from as date)
       and date_spine.date_day <  cast(coalesce(snapshot.dbt_valid_to, current_timestamp) as date) + 1

),

final as (

    select
        {{ dbt_utils.generate_surrogate_key(['active_days.posting_id', 'active_days.observed_date']) }} as fact_key,
        active_days.posting_id,
        active_days.observed_date                                as date_day,
        {{ dbt_utils.generate_surrogate_key(['active_days.company_name']) }}     as company_key,
        {{ dbt_utils.generate_surrogate_key(['active_days.location_display']) }} as location_key,
        active_days.job_title,
        active_days.salary_min,
        active_days.salary_max,
        active_days.apply_url,
        coalesce(sponsor_matched.is_verified_sponsor, false)      as is_verified_sponsor,
        coalesce(sponsor_matched.category, 'Unverified')          as sponsor_category

    from active_days
    left join sponsor_matched
        on active_days.posting_id = sponsor_matched.posting_id

)

select * from final
