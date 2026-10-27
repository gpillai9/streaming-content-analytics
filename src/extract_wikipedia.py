import requests
import datetime
import sys
from google.cloud import bigquery
wiki_records = []
client = bigquery.Client(project="streaming-content-analytics")
table_id = "streaming-content-analytics.wikipedia_raw.raw_article_pageviews"
query_headers = {
    "User-Agent": "StreamingContentAnalytics/1.0 (contact: govindpillai2002@gmail.com)"
}
response = requests.get("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/user/The_Dark_Knight/daily/2026100100/2026100700",
                        headers = query_headers)
if response.status_code != 200:
    sys.exit("API request failed.")

data = response.json()
for item in data["items"]:
    dictionary = {"article_title":item["article"],
                  "view_date":datetime.datetime.strptime(item["timestamp"],"%Y%m%d%H").date().isoformat(),
                  "views":item["views"]}
    wiki_records.append(dictionary)

job = client.load_table_from_json(wiki_records,table_id)
job.result()
print(wiki_records)