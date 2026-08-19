
    

    create  table
      "warehouse"."marts"."dim_skill__dbt_tmp"
  
    
    as (
      -- TODO (learning exercise — this is the "skills in demand" feature):
--
-- 1. Add a seeds/skill_keywords.csv with two columns: skill_name, pattern
--    (a regex or plain keyword to search for in the job description),
--    e.g. "dbt" / "\bdbt\b", "Python" / "\bpython\b", "Snowflake" /
--    "\bsnowflake\b", "Power BI" / "power\s?bi", etc. Seed it with the
--    10-15 tools that actually show up in the job specs you've been
--    reading (SQL, Python, dbt, Airflow, Snowflake, BigQuery, Looker,
--    Tableau, Power BI, Spark, Kafka, Terraform...).
--
-- 2. This model is then just: select * from "warehouse"."main"."skill_keywords"
--    plus a generated surrogate key.
--
-- 3. The interesting part is bridge_posting_skill.sql, which does the
--    actual regex matching of postings against this list — see that
--    file's TODO.

select
    md5(cast(coalesce(cast(skill_name as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as skill_key,
    skill_name,
    pattern
from "warehouse"."main"."skill_keywords"
    );
    
  