{#
    STRETCH GOAL macro stub — not wired into any model yet.

    Idea: given a company_name column and a reference to stg_sponsor_register,
    attempt a conservative match:
      1. Normalize both sides (lowercase, strip punctuation, strip a
         stopword list: ltd, limited, plc, group, holdings, international,
         uk, technologies, solutions, consulting, global...)
      2. Split into tokens.
      3. Only return a match when EVERY significant token (length >= 3,
         not a stopword) from company_name appears as a whole token in the
         register entry — not a substring match. See
         docs/sponsor_matching_notes.md for exactly why substring matching
         fails (the Zego/Azego, Sky/Sky Supermarket examples).
      4. When multiple register entries match, prefer the one with the
         fewest extra tokens (closest to an exact match) — but log/flag
         these as lower-confidence rather than silently picking one.

    DuckDB doesn't have a built-in fuzzy string match function as
    convenient as some warehouses' SOUNDEX/JAROWINKLER — you may end up
    doing the token comparison in a Python model (dbt supports Python
    models on some adapters) or precomputing candidate matches in a
    one-off Python script and loading the result as a seed, similar to how
    known_sponsor_matches.csv was built. Either approach is defensible;
    document which you chose and why.

    This is intentionally left unimplemented. Attempting it is a good
    "advanced" milestone once Phases 1-7 in PROJECT_PLAN.md are done.
#}

{% macro fuzzy_match_sponsor(company_name_column) %}
    {{ return(none) }}  {# placeholder — see docstring above #}
{% endmacro %}
