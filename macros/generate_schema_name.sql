{#
    dbt's default behaviour concatenates the target schema with any custom
    +schema config, e.g. a `marts` model in the `dev` target (schema "main")
    lands in a physical schema called `main_marts`, not `marts`. That
    would break the dashboard's raw SQL below (`select ... from
    marts.fct_job_postings`), which expects a clean `marts` schema name.
    This is dbt Labs' own documented override for exactly this case.
#}

{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}