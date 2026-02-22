{{
  config(
    materialized = 'table',
    tags = ['marts', 'metrics']
  )
}}

with repos as (
    select * from {{ ref('int_repo_growth_metrics') }}
),

-- Get top 5 repos per language using window function
ranked_repos as (
    select
        primary_language,
        full_name,
        stars_count,
        row_number() over (partition by primary_language order by stars_count desc) as repo_rank
    from repos
    where primary_language is not null
),

top_repos as (
    select 
        primary_language,
        array_agg(full_name order by stars_count desc) as top_5_repos
    from ranked_repos
    where repo_rank <= 5
    group by primary_language
),

language_stats as (
    select
        r.primary_language as language,
        
        -- Count metrics
        count(*) as repo_count,
        count(distinct r.owner) as unique_owners,
        
        -- Star metrics
        sum(r.stars_count) as total_stars,
        round(avg(r.stars_count), 0) as avg_stars,
        max(r.stars_count) as max_stars,
        approx_quantile(r.stars_count, 0.5) as median_stars,
        
        -- Fork metrics
        sum(r.forks_count) as total_forks,
        round(avg(r.forks_count), 0) as avg_forks,
        
        -- Activity metrics
        round(avg(r.stars_per_day), 2) as avg_stars_per_day,
        round(avg(r.repo_age_days), 0) as avg_repo_age_days,
        
        -- Top repositories
        tr.top_5_repos,
        
        -- Extract timestamp
        max(r.extracted_at) as extracted_at
        
    from repos r
    left join top_repos tr on r.primary_language = tr.primary_language
    where r.primary_language is not null
    group by r.primary_language, tr.top_5_repos
),

ranked as (
    select
        *,
        row_number() over (order by total_stars desc) as language_rank_by_stars,
        row_number() over (order by repo_count desc) as language_rank_by_repos,
        round(total_stars * 100.0 / sum(total_stars) over (), 2) as pct_of_total_stars
    from language_stats
)

select * from ranked
order by total_stars desc
