{{
  config(
    materialized = 'table',
    tags = ['marts', 'metrics']
  )
}}

-- Trending repos with ACTUAL star growth metrics (not lifetime average)

with repos as (
    select * from {{ ref('int_repo_growth_metrics') }}
),

star_growth as (
    select 
        repo_id,
        stars_gained_1d,
        stars_gained_7d,
        stars_gained_30d,
        avg_daily_stars_7d,
        avg_daily_stars_30d
    from {{ ref('fct_repo_star_growth') }}
),

categorized as (
    select
        r.*,
        sg.stars_gained_1d,
        sg.stars_gained_7d,
        sg.stars_gained_30d,
        sg.avg_daily_stars_7d,
        sg.avg_daily_stars_30d,
        
        -- AI category based on search query
        case
            when r.search_query in ('llm', 'large-language-model', 'langchain', 'openai') 
                then 'LLMs & Agents'
            when r.search_query in ('machine-learning', 'deep-learning', 'neural-network') 
                then 'Machine Learning'
            when r.search_query in ('nlp', 'natural-language-processing', 'transformers') 
                then 'NLP'
            when r.search_query in ('computer-vision') 
                then 'Computer Vision'
            when r.search_query in ('pytorch', 'tensorflow') 
                then 'Frameworks'
            else 'Other AI'
        end as ai_category
    from repos r
    left join star_growth sg on r.repo_id = sg.repo_id
)

select
    repo_id,
    full_name,
    repo_name,
    owner,
    description,
    html_url,
    primary_language,
    license_name,
    
    -- Categorization
    ai_category,
    search_query,
    
    -- Popularity metrics (backward compatibility)
    stars_count,
    popularity_tier,
    stars_per_day,
    
    -- ACTUAL star growth metrics (new)
    stars_gained_1d,
    stars_gained_7d,
    stars_gained_30d,
    avg_daily_stars_7d,
    avg_daily_stars_30d,
    
    -- Activity metrics
    activity_status,
    days_since_last_push,
    
    -- Repository metadata
    repo_age_days,
    created_at,
    pushed_at,
    extracted_at,
    
    -- Ranking within category (by total stars)
    row_number() over (partition by ai_category order by stars_count desc) as rank_in_category,
    
    -- Ranking by ACTUAL velocity (1-day growth, not lifetime average)
    row_number() over (order by stars_gained_1d desc nulls last) as rank_by_velocity
    
from categorized
order by stars_gained_1d desc nulls last
