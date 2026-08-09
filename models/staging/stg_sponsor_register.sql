-- TODO (learning exercise): mirror the pattern in stg_job_postings.sql —
-- {% if target.name == 'ci' %} select from {{ ref('sample_sponsor_register') }}
-- {% else %} select from {{ source('raw', 'sponsor_register') }} {% endif %}
--
-- Then rename/clean columns to snake_case:
--   "Organisation Name"  -> organisation_name (trim it — the raw register
--                           has leading/trailing whitespace on many rows,
--                           you'll fail a lot of joins if you don't trim)
--   "Town/City"           -> town_city
--   "County"               -> county
--   "Type & Rating"        -> type_and_rating   (e.g. "Worker (A rating)")
--   "Route"                 -> route             (e.g. "Skilled Worker")
--
-- Also worth doing here: parse the rating out of type_and_rating into its
-- own boolean `is_a_rated` column (only "A rating" sponsors are in good
-- standing — worth surfacing downstream).

select 1 as placeholder where false -- replace this whole model
