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
timestamp = now.strftime('%Y%m%d_%H%M%S')
project_root = (Path(__file__).resolve().parent.parent)
url = "https://api.themoviedb.org/3/movie/"
all_movies_url = url+"popular"
request_headers = {"Authorization": "Bearer " + my_api_key}
success_flag = True
data = []
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

movie_id = data[0]['results'][0]['id']
movie_url = url+str(movie_id)
query_parameters = {"language": "en-US"}
response = requests.get(movie_url,params=query_parameters,headers=request_headers)
if response.status_code != 200:
    print(response.status_code)
    sys.exit("API Request (individual movie) Failed. Terminating Script.")
else:
    movie_data = response.json()
print("Title: " + movie_data["title"])
print("Runtime: " + str(movie_data["runtime"]) + " minutes")
print("Budget: " + f"${movie_data["budget"]:,.2f}")
print("Production Companies: ",end="")
x = 0
for p in movie_data["production_companies"]:
    if(x == len(movie_data["production_companies"]) - 1):
        print(p['name'])
    else:        
        print(p['name'], end=", ")
        x += 1


    
    


