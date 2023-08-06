# Datagit

**Datagit** is a metric versionning library

```python
>>> from datagit import query_builder, github_connector
>>> from github import Github
>>> query = query_builder.build_query(table_id = "mrr_table", unique_key_columns= ["organisation_id", "date"])
'SELECT CONCAT(organisation_id, '__', date) AS unique_key, * FROM mrr_table WHERE TRUE ORDER BY 1'

>>> dataframe = bigquery.Client().query(query).to_dataframe() # Get a dataframe anyway you want
>>> github_connector.store_metric(Github("Token"), dataframe=dataframe, filename="data/act_metrics_finance/mrr", assignee=["Samox"])
'data/act_metrics_finance/mrr.csv pushed on production branch'
'Historical data change detected'
'Pull request was open from production to main, Samox was assigned to it'
```