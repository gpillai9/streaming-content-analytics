WITH cte AS (

SELECT ss.movie_id, ss.snapshot_date, ss.popularity, ss.popularity_rank, 
ss.vote_average, ss.vote_count, ss.page_number, ss.extract_timestamp, 
ss.ingestion_id, ss.release_date, 
DATE_DIFF(ss.snapshot_date,ss.release_date,DAY) AS days_since_release
,CONCAT(CAST(ss.movie_id AS STRING),"_",CAST(ss.snapshot_date AS STRING)) AS movie_snapshot_id
,ROW_NUMBER() OVER (PARTITION BY ss.movie_id, ss.snapshot_date ORDER BY ss.page_number DESC) AS ranking
FROM {{ref('stg_movie_snapshots')}} ss )

SELECT * EXCEPT (ranking)
FROM cte
WHERE ranking = 1
