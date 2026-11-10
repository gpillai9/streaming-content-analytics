import requests
import os
import sys
from dotenv import load_dotenv
from google.cloud import bigquery
from datetime import datetime, timezone
load_dotenv()
my_api_key = os.getenv("API_TOKEN")
request_headers = {"Authorization": "Bearer " + my_api_key}
client = bigquery.Client(project="streaming-content-analytics")
table_id = "streaming-content-analytics.tmdb_raw.movie_wikipedia_mapping"
wiki_headers = {
    "User-Agent": "StreamingContentAnalytics/1.0 (contact: govindpillai2002@gmail.com)"
}
movie_ids = []
job = client.query("SELECT DISTINCT SAFE_CAST(movie_id AS STRING) AS movie_id " \
"FROM `streaming-content-analytics.tmdb_raw.raw_movie_snapshots` " \
"WHERE movie_id NOT IN " \
"(SELECT DISTINCT tmdb_id " \
"FROM `streaming-content-analytics.tmdb_raw.movie_wikipedia_mapping`) " \
"AND movie_id NOT IN " \
"(SELECT tmdb_id " \
"FROM `streaming-content-analytics.tmdb_raw.movie_mapping_attempts` " \
"WHERE last_attempt > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY))")
response = job.result()
for row in response:
    movie_ids.append(row.movie_id)
print(f"Movies selected for mapping: {len(movie_ids)}")
movie_mappings = []
unsuccesful_attempts = []
for id in movie_ids:
    tmdb_link = "https://api.themoviedb.org/3/movie/" + id + "/external_ids"
    try: 
        response = requests.get(tmdb_link,headers=request_headers, timeout=15)
    except requests.exceptions.RequestException as e:
        print(f"TMDb request failed for movie {id}: {e}")
        dictionary = {"tmdb_id": int(id), "status": "TMDB_API_ERROR", "last_attempt": datetime.now(timezone.utc).isoformat(), "attempt_count":1}
        unsuccesful_attempts.append(dictionary)
        continue
    if response.status_code != 200:
        print("API request failed for movie " + id + ".")
        dictionary = {"tmdb_id": int(id), "status": "TMDB_API_ERROR", "last_attempt": datetime.now(timezone.utc).isoformat(), "attempt_count":1}
        unsuccesful_attempts.append(dictionary)
        continue
    data = response.json()
    wikidata_id = data.get("wikidata_id")
    if wikidata_id is None:
        print("No Wikidata ID found for " + id + ".")
        dictionary = {"tmdb_id": int(id), "status": "NO_WIKIDATA_ID", "last_attempt": datetime.now(timezone.utc).isoformat(), "attempt_count":1}
        unsuccesful_attempts.append(dictionary)
        continue
    wikilink = "https://www.wikidata.org/wiki/Special:EntityData/"+wikidata_id+".json"
    try:
        response2 = requests.get(wikilink, headers=wiki_headers, timeout=15)
    except requests.exceptions.RequestException as e:
        print(f"Wikidata request failed for movie {id}: {e}")
        dictionary = {"tmdb_id": int(id), "status": "WIKIDATA_API_ERROR", "last_attempt": datetime.now(timezone.utc).isoformat(), "attempt_count":1}
        unsuccesful_attempts.append(dictionary)
        continue
    if response2.status_code != 200:
        print(f"Wikidata request failed for {wikidata_id}: {response2.status_code}")
        dictionary = {"tmdb_id": int(id), "status": "WIKIDATA_API_ERROR", "last_attempt": datetime.now(timezone.utc).isoformat(), "attempt_count":1}
        unsuccesful_attempts.append(dictionary)
        continue
    data2 = response2.json()
    entity = data2.get("entities", {}).get(wikidata_id)

    if entity is None:
        print(f"Wikidata entity {wikidata_id} missing from response.")
        dictionary = {
            "tmdb_id": int(id),
            "status": "WIKIDATA_API_ERROR",
            "last_attempt": datetime.now(timezone.utc).isoformat(),
            "attempt_count": 1
        }
        unsuccesful_attempts.append(dictionary)
        continue

    wiki_sitelink = entity.get("sitelinks", {})
    enwiki = wiki_sitelink.get('enwiki')
    if(enwiki is None):
        print("No english Wikipedia page found for " + wikidata_id + ".")
        dictionary = {"tmdb_id": int(id), "status": "NO_ENWIKI_PAGE", "last_attempt": datetime.now(timezone.utc).isoformat(), "attempt_count":1}
        unsuccesful_attempts.append(dictionary)
        continue
    wiki_title = enwiki['title']
    mapping = {}
    mapping["tmdb_id"] = data['id']
    mapping["wikidata_id"] = wikidata_id
    mapping["wikipedia_title"] = wiki_title
    movie_mappings.append(mapping)
if movie_mappings:
    job = client.load_table_from_json(movie_mappings,table_id)
    job.result()
print(f"Inserted {len(movie_mappings)} movie mappings.")
print(f"Unsuccessful attempts: {len(unsuccesful_attempts)}")

attempts_table_id = "streaming-content-analytics.tmdb_raw.movie_mapping_attempts"

if unsuccesful_attempts:
    job = client.load_table_from_json(unsuccesful_attempts, attempts_table_id)
    job.result()
