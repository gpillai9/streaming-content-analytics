import os
from dotenv import load_dotenv

load_dotenv()

my_api_key = os.getenv("API_TOKEN")
print(my_api_key)