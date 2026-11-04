import requests
import datetime
import urllib
from google.cloud import bigquery

wiki_records = []
table_id = "streaming-content-analytics.wikipedia_raw.raw_article_pageviews"
now = datetime.datetime.now(datetime.timezone.utc)
past = now - datetime.timedelta(days=2)
fpast = past.strftime("%Y%m%d00")
target_date = past.date().isoformat()
client = bigquery.Client(project="streaming-content-analytics")
query_headers = {
    "User-Agent": "StreamingContentAnalytics/1.0 (contact: govindpillai2002@gmail.com)"
}
parameter = bigquery.ScalarQueryParameter("target_date", "DATE", target_date)
job_config = bigquery.QueryJobConfig(
    query_parameters = [parameter]
)
job = client.query("SELECT article_title " \
"FROM `streaming-content-analytics.wikipedia_raw.raw_article_pageviews` " \
"WHERE view_date = @target_date", job_config)
existing_records = job.result()
existing_titles = {row.article_title for row in existing_records}
job = client.query("" \
"SELECT tmdb_id, wikipedia_title " \
"FROM `streaming-content-analytics.tmdb_raw.movie_wikipedia_mapping`")
response = job.result()

for row in response:
    if row.wikipedia_title.replace(" ", "_") in existing_titles:
        print("movie already exists in data.")
        continue
    wikititle = urllib.parse.quote(row.wikipedia_title)
    wikilink = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/user/" + wikititle + "/daily/"+fpast+"/"+fpast
    res = requests.get(wikilink, headers = query_headers)
    if res.status_code != 200:
        print(row.wikipedia_title, res.status_code)
        continue
    data = res.json()
    for item in data["items"]:
        dictionary = {"article_title":item["article"],
                    "view_date":datetime.datetime.strptime(item["timestamp"],"%Y%m%d%H").date().isoformat(),
                    "views":item["views"]}
        wiki_records.append(dictionary)
if(len(wiki_records) > 0):
    job = client.load_table_from_json(wiki_records, table_id)
    job.result()
print(f"Inserted {len(wiki_records)} Wikipedia pageview records.")