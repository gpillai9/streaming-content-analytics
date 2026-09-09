import requests
import os
import sys
import json
from dotenv import load_dotenv
from datetime import datetime, timezone
from pathlib import Path

load_dotenv()

my_api_key = os.getenv("API_TOKEN")
now = datetime.now(timezone.utc)
query_parameters = {}
timestamp = now.strftime('%Y%m%d_%H%M%S')
project_root = (Path(__file__).resolve().parent.parent)
url = "https://api.themoviedb.org/3/movie/"
metadata_url = ""
all_movies_url = url+"popular"
request_headers = {"Authorization": "Bearer " + my_api_key}
success_flag = True
data = []
metadata = []
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
with open(f'{project_root}/data/raw/movies_{timestamp}.json','w') as f:
    json.dump(data, f, indent=2)

for page in data:
    for movie in page['results']:
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

with open(f'{project_root}/data/metadata/movies.json','w') as f:
    json.dump(metadata, f, indent=2)

    
    


