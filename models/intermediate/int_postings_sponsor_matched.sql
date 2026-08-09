-- Joins postings to the curated sponsor match seed (see
-- docs/sponsor_matching_notes.md for why this is a curated lookup rather
-- than a pure fuzzy-match — precision over recall).
--
-- STRETCH GOAL (not required for a working pipeline): for company_name
-- values with no match in the seed, fall through to the
-- fuzzy_match_sponsor() macro stub in macros/fuzzy_match_sponsor.sql and
-- have it attempt a conservative multi-token match against
-- stg_sponsor_register, returning null rather than a low-confidence guess.
-- This is genuinely a hard, interesting problem — don't feel obligated to
-- solve it perfectly; even documenting why you *didn't* fully automate it
-- (see docs/sponsor_matching_notes.md) is a legitimate engineering story.

with postings as (

    select * from {{ ref('stg_job_postings') }}

),

known_matches as (

    select * from {{ ref('known_sponsor_matches') }}

),

joined as (

    select
        postings.posting_id,
        postings.job_title,
        postings.company_name,
        postings.location_display,
        postings.salary_min,
        postings.salary_max,
        postings.apply_url,
        postings.posted_at,
        known_matches.sponsor_entity,
        known_matches.category,
        (known_matches.sponsor_entity is not null) as is_verified_sponsor

    from postings
    left join known_matches
        on postings.company_name = known_matches.company_name_raw

)

select * from joined
