import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timezone
from pathlib import Path

load_dotenv()

my_api_key = os.getenv("API_TOKEN")
now = datetime.now(timezone.utc)
timestamp = now.strftime('%Y%m%d_%H%M%S')
project_root = (Path(__file__).resolve().parent.parent)
url = "https://api.themoviedb.org/3/movie/popular"
request_headers = {"Authorization": "Bearer " + my_api_key}
success_flag = True
data = []
for page_number in range(1,26):
    query_parameters = {"language": "en-US", "page":page_number}
    response = requests.get(url,params=query_parameters,headers=request_headers)
    if response.status_code != 200:
        print(response.status_code)
        success_flag = False
        break
    else:
        data.append(response.json())
if success_flag:
    with open(f'{project_root}/data/raw/movies_{timestamp}.json','w') as f:
        json.dump(data, f, indent=2)
    


