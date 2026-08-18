import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timezone
from pathlib import Path

load_dotenv()

my_api_key = os.getenv("API_TOKEN")
url = "https://api.themoviedb.org/3/movie/popular"
query_parameters = {"language": "en-US", "page":1}
request_headers = {"Authorization": "Bearer " + my_api_key} 

response = requests.get(url,params=query_parameters,headers=request_headers)

if response.status_code != 200:
    print(response.status_code)
else:
    data = response.json()
    now = datetime.now(timezone.utc)
    timestamp = now.strftime('%Y%m%d_%H%M%S')
    file_path = (Path(__file__).resolve().parent.parent)
    with open(f'{file_path}/data/raw/movies_{timestamp}.json','w') as f:
        json.dump(data, f)
    


