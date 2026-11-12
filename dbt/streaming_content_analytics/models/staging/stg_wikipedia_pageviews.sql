SELECT article_title, view_date, views
FROM {{source('wikipedia_raw','raw_article_pageviews')}}