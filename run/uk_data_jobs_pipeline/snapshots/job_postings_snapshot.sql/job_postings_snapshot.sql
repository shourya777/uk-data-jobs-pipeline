
      update "warehouse"."snapshots"."job_postings_snapshot" as DBT_INTERNAL_TARGET
    set dbt_valid_to = DBT_INTERNAL_SOURCE.dbt_valid_to
    from "job_postings_snapshot__dbt_tmp20260820074330707780" as DBT_INTERNAL_SOURCE
    where DBT_INTERNAL_SOURCE.dbt_scd_id::text = DBT_INTERNAL_TARGET.dbt_scd_id::text
      and DBT_INTERNAL_SOURCE.dbt_change_type::text in ('update'::text, 'delete'::text)
      
        and DBT_INTERNAL_TARGET.dbt_valid_to is null;
      

    insert into "warehouse"."snapshots"."job_postings_snapshot" ("posting_id", "job_title", "company_name", "location_display", "salary_min", "salary_max", "apply_url", "posted_at", "dbt_updated_at", "dbt_valid_from", "dbt_valid_to", "dbt_scd_id")
    select DBT_INTERNAL_SOURCE."posting_id",DBT_INTERNAL_SOURCE."job_title",DBT_INTERNAL_SOURCE."company_name",DBT_INTERNAL_SOURCE."location_display",DBT_INTERNAL_SOURCE."salary_min",DBT_INTERNAL_SOURCE."salary_max",DBT_INTERNAL_SOURCE."apply_url",DBT_INTERNAL_SOURCE."posted_at",DBT_INTERNAL_SOURCE."dbt_updated_at",DBT_INTERNAL_SOURCE."dbt_valid_from",DBT_INTERNAL_SOURCE."dbt_valid_to",DBT_INTERNAL_SOURCE."dbt_scd_id"
    from "job_postings_snapshot__dbt_tmp20260820074330707780" as DBT_INTERNAL_SOURCE
    where DBT_INTERNAL_SOURCE.dbt_change_type::text = 'insert'::text;


  