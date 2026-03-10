{{
  config(
    materialized = 'incremental',
    tags = ['marts', 'metrics', 'star_history'],
    unique_key = ['repo_id', 'snapshot_date'],
    incremental_strategy = 'merge',
    merge_update_columns = ['stars_count', 'snapshot_time', 'extracted_at', 'previous_stars', 'previous_date', 'days_since_last_snapshot', 'stars_gained_1d'],
    pre_hook = "
      {% if is_incremental() %}
        ALTER TABLE {{ this }} ADD COLUMN IF NOT EXISTS snapshot_time TIMESTAMP;
      {% endif %}
    "
  )
}}

-- Daily snapshot of repository star counts
-- Tracks actual star growth over time for accurate velocity metrics
-- IDEMPOTENT: One snapshot per day, but updates to latest values on re-runs

with current_data as (
    select
        repo_id,
        full_name,
        stars_count,
        current_date as snapshot_date,
        current_timestamp as snapshot_time,
        extracted_at
    from {{ ref('int_repo_growth_metrics') }}
),

{% if is_incremental() %}
-- Get the most recent previous snapshot within the last 3 days
-- Resilient to pipeline gaps: if yesterday failed, uses the last available snapshot
previous_snapshot as (
    select
        repo_id,
        stars_count as previous_stars,
        snapshot_date as previous_date
    from (
        select
            repo_id,
            stars_count,
            snapshot_date,
            row_number() over (partition by repo_id order by snapshot_date desc) as rn
        from {{ this }}
        where snapshot_date >= current_date - interval '3 days'
          and snapshot_date < current_date
    ) ranked
    where rn = 1
),
{% else %}
-- First run: empty previous snapshot
previous_snapshot as (
    select
        null::bigint as repo_id,
        null::bigint as previous_stars,
        null::date as previous_date
    where false
),
{% endif %}

-- Calculate daily star gains
calculated as (
    select
        c.repo_id,
        c.full_name,
        c.stars_count,
        c.snapshot_date,
        c.snapshot_time,
        c.extracted_at,

        -- Previous snapshot info
        p.previous_stars,
        p.previous_date,

        -- Actual days elapsed since last snapshot (may be >1 if pipeline had a gap)
        case
            when p.previous_date is not null
            then (c.snapshot_date - p.previous_date)
            else null
        end as days_since_last_snapshot,

        -- Stars gained since last available snapshot
        case
            when p.previous_stars is not null
            then c.stars_count - p.previous_stars
            else null
        end as stars_gained_1d

    from current_data c
    left join previous_snapshot p on c.repo_id = p.repo_id
)

select * from calculated
