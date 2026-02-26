{{
  config(
    materialized = 'incremental',
    tags = ['marts', 'metrics', 'star_history'],
    unique_key = ['repo_id', 'snapshot_date'],
    incremental_strategy = 'merge'
  )
}}

-- Daily snapshot of repository star counts
-- Tracks actual star growth over time for accurate velocity metrics

with current_data as (
    select
        repo_id,
        full_name,
        stars_count,
        current_date as snapshot_date,
        extracted_at
    from {{ ref('int_repo_growth_metrics') }}
),

{% if is_incremental() %}
-- Get yesterday's snapshot for comparison (only in incremental mode)
previous_snapshot as (
    select
        repo_id,
        stars_count as previous_stars,
        snapshot_date as previous_date
    from {{ this }}
    where snapshot_date = current_date - interval '1 day'
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
        c.extracted_at,
        
        -- Previous snapshot
        p.previous_stars,
        
        -- Stars gained since yesterday
        case 
            when p.previous_stars is not null 
            then c.stars_count - p.previous_stars
            else null
        end as stars_gained_1d
        
    from current_data c
    left join previous_snapshot p on c.repo_id = p.repo_id
)

select * from calculated

{% if is_incremental() %}
-- Only insert/update today's snapshot
where snapshot_date = current_date
{% endif %}
