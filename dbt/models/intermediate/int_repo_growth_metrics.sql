{{
  config(
    materialized = 'view',
    tags = ['intermediate']
  )
}}

with repos as (
    select * from {{ ref('stg_repositories') }}
),

metrics as (
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
        
        -- Star metrics
        stars_count,
        stars_per_day,
        case
            when stars_count >= 10000 then '⭐⭐⭐⭐⭐ Mega'
            when stars_count >= 5000 then '⭐⭐⭐⭐ Very Popular'
            when stars_count >= 1000 then '⭐⭐⭐ Popular'
            when stars_count >= 500 then '⭐⭐ Growing'
            else '⭐ New'
        end as popularity_tier,
        
        -- Engagement metrics
        forks_count,
        open_issues_count,
        round(stars_count / nullif(forks_count, 0), 2) as star_to_fork_ratio,
        
        -- Activity indicators
        repo_age_days,
        date_diff('day', pushed_at, current_date) as days_since_last_push,
        case
            when days_since_last_push <= 7 then 'Very Active'
            when days_since_last_push <= 30 then 'Active'
            when days_since_last_push <= 90 then 'Moderate'
            else 'Stale'
        end as activity_status,
        
        -- Repository health
        is_fork,
        is_archived,
        
        -- Search context
        search_query,
        
        -- AI Category classification
        case
            when search_query in ('llm', 'large-language-model', 'gpt-5', 'claude-opus', 'gemini-pro', 'grok-xai', 'kimi-k2', 'kimi-k2.5', 'deepseek-v3', 'qwen3', 'llama-4', 'glm-4', 'mistral-lechat', 'open-source-llm', 'openai-api') 
                then 'LLMs'
            when search_query in ('langchain', 'langgraph', 'llamaindex', 'autogen', 'crewai', 'openclaw', 'agentic-ai')
                then 'Agents & RAG'
            when search_query in ('machine-learning', 'deep-learning', 'neural-network', 'fine-tuning', 'lora-peft') 
                then 'Machine Learning'
            when search_query in ('nlp', 'natural-language-processing', 'transformers') 
                then 'NLP'
            when search_query in ('computer-vision', 'multimodal-ai') 
                then 'Vision & Multimodal'
            when search_query in ('pytorch', 'tensorflow', 'keras', 'jax') 
                then 'Deep Learning Frameworks'
            when search_query in ('vector-database', 'rag', 'mlops') 
                then 'Infrastructure & Tools'
            when search_query in ('huggingface')
                then 'AI Platforms & Hubs'
            when search_query in ('ollama')
                then 'Local LLM Deployment'
            when search_query in ('artificial-intelligence', 'ai')
                then 'General AI'
            else 'Other'
        end as ai_category,
        
        -- Timestamps
        created_at,
        updated_at,
        pushed_at,
        extracted_at
        
    from repos
    where not is_fork  -- Focus on original repositories
      and not is_archived  -- Exclude archived repos
)

select * from metrics
