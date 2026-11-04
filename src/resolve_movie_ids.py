import requests
import os
import sys
from dotenv import load_dotenv
from google.cloud import bigquery
load_dotenv()
my_api_key = os.getenv("API_TOKEN")
request_headers = {"Authorization": "Bearer " + my_api_key}
client = bigquery.Client(project="streaming-content-analytics")
table_id = "streaming-content-analytics.tmdb_raw.movie_wikipedia_mapping"
wiki_headers = {
    "User-Agent": "StreamingContentAnalytics/1.0 (contact: govindpillai2002@gmail.com)"
}
movie_ids = ['27205', '438631', '155', '597', '603']
movie_mappings = []
for id in movie_ids:
    tmdb_link = "https://api.themoviedb.org/3/movie/" + id + "/external_ids"
    response = requests.get(tmdb_link,headers=request_headers)
    data = response.json()
    wikidata_id = data.get("wikidata_id")
    if wikidata_id is None:
        print("No Wikidata ID found for " + id + ".")
        continue
    wikilink = "https://www.wikidata.org/wiki/Special:EntityData/"+wikidata_id+".json"
    response2 = requests.get(wikilink, headers=wiki_headers)
    data2 = response2.json()
    wiki_sitelink = data2['entities'][wikidata_id]['sitelinks']
    enwiki = wiki_sitelink.get('enwiki')
    if(enwiki is None):
        print("No english Wikipedia page found for " + wikidata_id + ".")
        continue
    wiki_title = enwiki['title']
    mapping = {}
    mapping["tmdb_id"] = data['id']
    mapping["wikidata_id"] = wikidata_id
    mapping["wikipedia_title"] = wiki_title
    movie_mappings.append(mapping)
job = client.load_table_from_json(movie_mappings,table_id)
job.result()