{{
  config(
    materialized = 'view',
    tags = ['staging']
  )
}}

with source as (
    select * from {{ source('github_raw', 'repositories') }}
),

renamed as (
    select
        -- Primary key
        id as repo_id,
        
        -- Repository identifiers
        full_name,
        name as repo_name,
        owner__login as owner,
        owner__type as owner_type,
        
        -- Repository metadata
        description,
        html_url,
        homepage,
        
        -- Popularity metrics
        stargazers_count as stars_count,
        watchers_count as watchers_count,
        forks_count,
        open_issues_count,
        
        -- Language and topics
        language as primary_language,
        
        -- Repository characteristics
        private as is_private,
        fork as is_fork,
        archived as is_archived,
        disabled as is_disabled,
        
        -- Size and complexity
        size as repo_size_kb,
        
        -- License information
        license__name as license_name,
        license__spdx_id as license_spdx_id,
        
        -- Timestamps
        created_at,
        updated_at,
        pushed_at,
        
        -- Search metadata
        search_query,
        
        -- Audit columns
        _dlt_load_id,
        _dlt_extracted_at as extracted_at,
        
        -- Calculated fields
        date_diff('day', created_at, current_date) as repo_age_days,
        stars_count / nullif(date_diff('day', created_at, current_date), 0) as stars_per_day
        
    from source
)

select * from renamed
