{{
  config(
    materialized = 'view',
    tags = ['marts', 'metrics', 'star_growth']
  )
}}

-- Calculate actual star growth over different time periods
-- Uses daily snapshots to show real velocity (not lifetime average)

with current_snapshot as (
    select
        repo_id,
        full_name,
        stars_count,
        stars_gained_1d,
        days_since_last_snapshot,
        snapshot_date
    from {{ ref('fct_repo_star_history') }}
    where snapshot_date = current_date
),

-- Most recent snapshot within ±2 days of 7 days ago (resilient to gaps)
snapshot_7d_ago as (
    select
        repo_id,
        stars_count as stars_7d_ago,
        snapshot_date as snapshot_date_7d
    from (
        select
            repo_id,
            stars_count,
            snapshot_date,
            row_number() over (
                partition by repo_id
                order by abs(date_diff('day', snapshot_date, current_date - interval '7 days'))
            ) as rn
        from {{ ref('fct_repo_star_history') }}
        where snapshot_date between current_date - interval '9 days'
                                and current_date - interval '5 days'
    ) ranked
    where rn = 1
),

-- Most recent snapshot within ±2 days of 30 days ago (resilient to gaps)
snapshot_30d_ago as (
    select
        repo_id,
        stars_count as stars_30d_ago,
        snapshot_date as snapshot_date_30d
    from (
        select
            repo_id,
            stars_count,
            snapshot_date,
            row_number() over (
                partition by repo_id
                order by abs(date_diff('day', snapshot_date, current_date - interval '30 days'))
            ) as rn
        from {{ ref('fct_repo_star_history') }}
        where snapshot_date between current_date - interval '32 days'
                                and current_date - interval '28 days'
    ) ranked
    where rn = 1
),

joined as (
    select
        c.repo_id,
        c.full_name,
        c.stars_count as current_stars,
        c.stars_gained_1d,
        c.days_since_last_snapshot,
        c.snapshot_date,

        -- 7-day growth (using closest available snapshot near 7d ago)
        s7.stars_7d_ago,
        case
            when s7.stars_7d_ago is not null
            then c.stars_count - s7.stars_7d_ago
            else null
        end as stars_gained_7d,

        -- 30-day growth (using closest available snapshot near 30d ago)
        s30.stars_30d_ago,
        case
            when s30.stars_30d_ago is not null
            then c.stars_count - s30.stars_30d_ago
            else null
        end as stars_gained_30d,

        -- Average daily velocity (7-day), divided by actual elapsed days
        case
            when s7.stars_7d_ago is not null
            then round(
                (c.stars_count - s7.stars_7d_ago)
                / nullif((c.snapshot_date - s7.snapshot_date_7d), 0)::numeric,
                1
            )
            else null
        end as avg_daily_stars_7d,

        -- Average daily velocity (30-day), divided by actual elapsed days
        case
            when s30.stars_30d_ago is not null
            then round(
                (c.stars_count - s30.stars_30d_ago)
                / nullif((c.snapshot_date - s30.snapshot_date_30d), 0)::numeric,
                1
            )
            else null
        end as avg_daily_stars_30d

    from current_snapshot c
    left join snapshot_7d_ago s7 on c.repo_id = s7.repo_id
    left join snapshot_30d_ago s30 on c.repo_id = s30.repo_id
)

select * from joined
order by stars_gained_7d desc nulls last
