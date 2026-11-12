SELECT tmdb_id, wikidata_id, wikipedia_title
FROM {{source('tmdb_raw','movie_wikipedia_mapping')}}