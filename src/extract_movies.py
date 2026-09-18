import requests
import os
import sys
import uuid
import json
from dotenv import load_dotenv
from datetime import datetime, timezone
from pathlib import Path
from google.cloud import bigquery

load_dotenv()
client = bigquery.Client(project="streaming-content-analytics")
my_api_key = os.getenv("API_TOKEN")
now = datetime.now(timezone.utc)
extracted_at = now
snapshot_date = now.date()
query_parameters = {}
timestamp = now.strftime('%Y%m%d_%H%M%S')
project_root = (Path(__file__).resolve().parent.parent)
url = "https://api.themoviedb.org/3/movie/"
source_file_name = f"movies_{timestamp}.json"
metadata_url = ""
all_movies_url = url+"popular"
my_uuid = str(uuid.uuid4())
request_headers = {"Authorization": "Bearer " + my_api_key}
success_flag = True
data = []
metadata = []
metadata_bq = []
snapshot_rows = []
known_movie_ids = set()
with open(f'{project_root}/data/metadata/movies.json','r') as f:
    metadata = json.load(f)
for movie in metadata:
    known_movie_ids.add(movie["id"])
for page_number in range(1,26):
    query_parameters = {"language": "en-US", "page":page_number}
    response = requests.get(all_movies_url,params=query_parameters,headers=request_headers)
    if response.status_code != 200:
        print(response.status_code)
        success_flag = False
        break
    else:
        data.append(response.json())
if success_flag == False:
    sys.exit("API Request (all movies) Failed. Terminating Script.")
with open(project_root / "data" / "raw" / source_file_name,'w') as f:
    json.dump(data, f, indent=2)


metadata_now = datetime.now(timezone.utc)
metadata_uuid = str(uuid.uuid4())
for page in data:
    for position, movie in enumerate(page["results"], start=1):
        snapshot_movie = movie.copy()
        snapshot_movie["movie_id"] = snapshot_movie.pop("id")
        snapshot_movie["extract_timestamp"] = str(extracted_at)
        snapshot_movie["snapshot_date"] = str(snapshot_date)
        snapshot_movie["snapshot_file_name"] = source_file_name
        snapshot_movie["page_number"] = page["page"]
        snapshot_movie["popularity_rank"] = ((page["page"] - 1) * 20) + position
        snapshot_movie["ingestion_id"] = my_uuid
        snapshot_movie.pop("backdrop_path")
        snapshot_movie.pop("poster_path")
        snapshot_rows.append(snapshot_movie)
        if(movie["id"] not in known_movie_ids):
            metadata_url = url + str(movie["id"])
            query_parameters = {"language": "en-US"}
            response = requests.get(metadata_url,params=query_parameters,headers=request_headers)
            if response.status_code != 200:
                print(response.status_code)
                sys.exit("API Request (individual movie) Failed. Terminating Script.")
            metadata.append(response.json())
            known_movie_ids.add(movie["id"])
            print("New movie added!")

loaded_at = datetime.now(timezone.utc)
for movie in snapshot_rows:
    movie["load_timestamp"] = str(loaded_at)
table_id = "streaming-content-analytics.tmdb_raw.raw_movie_snapshots"
job = client.load_table_from_json(snapshot_rows, table_id)
job.result()
with open(f'{project_root}/data/metadata/movies.json','w') as f:
    json.dump(metadata, f, indent=2)

for movie in metadata:
    metadata_to_load = {}
    metadata_to_load["movie_id"] = movie["id"]
    metadata_to_load["title"] = movie["title"]
    metadata_to_load["budget"] = movie["budget"]
    metadata_to_load["revenue"] = movie["revenue"]
    metadata_to_load["status"] = movie["status"]
    metadata_to_load["tagline"] = movie["tagline"]
    metadata_to_load["imdb_id"] = movie["imdb_id"]
    metadata_to_load["runtime"] = movie["runtime"]
    metadata_to_load["collection_id"] = movie["belongs_to_collection"]["id"] if movie["belongs_to_collection"] is not None else None
    metadata_to_load["collection_name"] = movie["belongs_to_collection"]["name"] if movie["belongs_to_collection"] is not None else None
    metadata_to_load["genres"] = movie["genres"]
    metadata_to_load["origin_country"] = movie["origin_country"]
    metadata_to_load["production_companies"] = [
    {
        "id": company["id"],
        "name": company["name"],
        "origin_country": company["origin_country"]
    }
    for company in movie["production_companies"]
]
    metadata_to_load["production_countries"] = [m["iso_3166_1"] for m in movie["production_countries"]]
    metadata_to_load["spoken_languages"] = [m["english_name"] for m in movie["spoken_languages"]]
    metadata_to_load["ingestion_timestamp"] = str(metadata_now)
    metadata_to_load["ingestion_id"] = metadata_uuid
    metadata_to_load["enrichment_timestamp"] = str(metadata_now)
    metadata_bq.append(metadata_to_load)
'''
table_id = "streaming-content-analytics.tmdb_raw.raw_movie_metadata"
job = client.load_table_from_json(metadata_bq, table_id)
job.result()
'''

