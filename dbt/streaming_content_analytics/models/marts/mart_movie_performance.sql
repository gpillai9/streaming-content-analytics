WITH cte AS (
    SELECT
        md.title,
        f.movie_id,
        f.snapshot_date,
        f.popularity_rank,
        f.popularity,
        LAG(f.popularity_rank) OVER (
            PARTITION BY f.movie_id
            ORDER BY f.snapshot_date
        ) AS previous_rank,
        LAG(f.popularity) OVER (
            PARTITION BY f.movie_id
            ORDER BY f.snapshot_date
        ) AS previous_popularity,
        LAG(f.snapshot_date) OVER (
            PARTITION BY f.movie_id
            ORDER BY f.snapshot_date
        ) AS previous_snapshot_date
    FROM {{ ref('fct_movie_daily') }} f
    LEFT JOIN {{ ref('stg_movie_metadata') }} md
        ON f.movie_id = md.movie_id
),

performance AS (
    SELECT
        *,
        previous_rank - popularity_rank AS rank_movement,
        popularity - previous_popularity AS popularity_change,
        DATE_DIFF(
            snapshot_date,
            previous_snapshot_date,
            DAY
        ) AS days_between_snapshots
    FROM cte
)

SELECT
    *,
    CASE
        WHEN previous_snapshot_date IS NULL THEN 'New Entry'
        WHEN days_between_snapshots > 1 THEN 'Returning'
        WHEN rank_movement > 0 THEN 'Rising'
        WHEN rank_movement < 0 THEN 'Falling'
        ELSE 'Unchanged'
    END AS trend_category
FROM performance