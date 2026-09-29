SELECT movie_id, title, budget, revenue, 
status, tagline, imdb_id, runtime, collection_id, 
collection_name, genres, origin_country, production_companies, 
production_countries, spoken_languages, ingestion_timestamp, 
ingestion_id, enrichment_timestamp
FROM {{source('tmdb_raw','raw_movie_metadata')}}