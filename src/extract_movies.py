import requests
import os
from dotenv import load_dotenv

load_dotenv()

my_api_key = os.getenv("API_TOKEN")
url = "https://api.themoviedb.org/3/movie/popular"
query_parameters = {"language": "en-US", "page":1}
request_headers = {"Authorization": "Bearer " + my_api_key} 

response = requests.get(url,params=query_parameters,headers=request_headers)

print(response.json())

