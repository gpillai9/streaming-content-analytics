WITH cte AS (
    SELECT
        title,
        movie_id,
        snapshot_date,
        popularity_rank,
		popularity,
        LAG(popularity_rank) OVER (
            PARTITION BY movie_id
            ORDER BY snapshot_date
        ) AS previous_rank,
		LAG(popularity) OVER (
			PARTITION BY movie_id
			ORDER BY snapshot_date
		) AS previous_popularity,
		LAG(snapshot_date) OVER (
			PARTITION BY movie_id
			ORDER BY snapshot_date
		) AS previous_snapshot_date
    FROM {{ ref('fct_movie_daily') }}
)

SELECT
    *,
    previous_rank - popularity_rank AS rank_movement,
	popularity - previous_popularity AS popularity_change,
	DATE_DIFF(snapshot_date, previous_snapshot_date, DAY) AS days_between_snapshots
FROM cte