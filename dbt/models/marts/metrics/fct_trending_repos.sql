{{
  config(
    materialized = 'table',
    tags = ['marts', 'metrics']
  )
}}

with repos as (
    select * from {{ ref('int_repo_growth_metrics') }}
),

categorized as (
    select
        *,
        -- AI category based on search query
        case
            when search_query in ('llm', 'large-language-model', 'langchain', 'openai') 
                then 'LLMs & Agents'
            when search_query in ('machine-learning', 'deep-learning', 'neural-network') 
                then 'Machine Learning'
            when search_query in ('nlp', 'natural-language-processing', 'transformers') 
                then 'NLP'
            when search_query in ('computer-vision') 
                then 'Computer Vision'
            when search_query in ('pytorch', 'tensorflow') 
                then 'Frameworks'
            else 'Other AI'
        end as ai_category
    from repos
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
    
    -- Popularity metrics
    stars_count,
    popularity_tier,
    stars_per_day,
    
    -- Activity metrics
    activity_status,
    days_since_last_push,
    
    -- Repository metadata
    repo_age_days,
    created_at,
    pushed_at,
    extracted_at,
    
    -- Ranking within category
    row_number() over (partition by ai_category order by stars_count desc) as rank_in_category,
    row_number() over (order by stars_per_day desc nulls last) as rank_by_velocity
    
from categorized
order by stars_count desc
