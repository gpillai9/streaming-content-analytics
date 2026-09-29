SELECT movie_id
,title
,original_title
,original_language
,release_date
,genre_ids
,adult
,video
,popularity
,popularity_rank
,vote_average
,vote_count
,snapshot_date
,page_number
,extract_timestamp
,load_timestamp
,ingestion_id
,snapshot_file_name 
FROM {{source('tmdb_raw', 'raw_movie_snapshots')}}