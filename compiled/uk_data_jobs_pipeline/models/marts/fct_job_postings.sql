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

    select * from "warehouse"."snapshots"."job_postings_snapshot"

),

sponsor_matched as (

    select posting_id, sponsor_entity, category, is_verified_sponsor
    from "warehouse"."intermediate"."int_postings_sponsor_matched"

),

date_spine as (

    





with rawdata as (

    

    

    with p as (
        select 0 as generated_number union all select 1
    ), unioned as (

    select

    
    p0.generated_number * power(2, 0)
     + 
    
    p1.generated_number * power(2, 1)
     + 
    
    p2.generated_number * power(2, 2)
     + 
    
    p3.generated_number * power(2, 3)
     + 
    
    p4.generated_number * power(2, 4)
     + 
    
    p5.generated_number * power(2, 5)
     + 
    
    p6.generated_number * power(2, 6)
     + 
    
    p7.generated_number * power(2, 7)
     + 
    
    p8.generated_number * power(2, 8)
     + 
    
    p9.generated_number * power(2, 9)
    
    
    + 1
    as generated_number

    from

    
    p as p0
     cross join 
    
    p as p1
     cross join 
    
    p as p2
     cross join 
    
    p as p3
     cross join 
    
    p as p4
     cross join 
    
    p as p5
     cross join 
    
    p as p6
     cross join 
    
    p as p7
     cross join 
    
    p as p8
     cross join 
    
    p as p9
    
    

    )

    select *
    from unioned
    where generated_number <= 729
    order by generated_number



),

all_periods as (

    select (
        

    (cast('2026-01-01' as date) + cast(row_number() over (order by generated_number) - 1 as bigint) * interval 1 day)
    ) as date_day
    from rawdata

),

filtered as (

    select *
    from all_periods
    where date_day <= cast('2027-12-31' as date)

)

select * from filtered



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
        md5(cast(coalesce(cast(active_days.posting_id as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(active_days.observed_date as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as fact_key,
        active_days.posting_id,
        active_days.observed_date                                as date_day,
        md5(cast(coalesce(cast(active_days.company_name as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT))     as company_key,
        md5(cast(coalesce(cast(active_days.location_display as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as location_key,
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