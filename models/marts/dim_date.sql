-- Standard date dimension, generated with the dbt_date package rather
-- than hand-written — don't reinvent this, every warehouse project needs
-- one and it's a solved problem. get_date_dimension() already provides
-- date_day, day_of_week, year, month, quarter, etc. — we only add
-- is_weekend on top. Range covers the project's realistic lifetime;
-- extend end_date if you're still running this a year from now.

with base as (

    {{ dbt_date.get_date_dimension('2026-01-01', '2027-12-31') }}

)

select
    base.*,
    (date_part('dow', base.date_day) in (0, 6)) as is_weekend
from base
