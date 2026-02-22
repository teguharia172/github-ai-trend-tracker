{{
  config(
    materialized = 'table',
    tags = ['marts', 'core'],
    unique_key = 'repo_id'
  )
}}

select
    repo_id,
    full_name,
    repo_name,
    owner,
    owner_type,
    description,
    html_url,
    primary_language,
    license_name,
    
    -- Metrics
    stars_count,
    popularity_tier,
    forks_count,
    open_issues_count,
    star_to_fork_ratio,
    
    -- Activity
    repo_age_days,
    days_since_last_push,
    activity_status,
    
    -- Classification
    search_query,
    
    -- Timestamps
    created_at,
    updated_at,
    pushed_at,
    extracted_at,
    current_timestamp as dbt_loaded_at

from {{ ref('int_repo_growth_metrics') }}
