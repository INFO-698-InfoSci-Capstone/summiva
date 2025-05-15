from elasticsearch import Elasticsearch
from src.config.config import settings

# Create the Elasticsearch client without timeout parameter
# In newer Elasticsearch client versions, timeout should be applied on operations
es = Elasticsearch(hosts=[settings.ELASTIC_URL])

def keyword_search(query: str, filters: dict = None, size=10):
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["summary_text", "tags", "title"]
            }
        }
    }
    res = es.search(index="summiva_docs", body=body, size=size)
    return [
        {
            "doc_id": hit["_id"],
            "score": hit["_score"],
            "snippet": hit["_source"].get("summary_text", "")[:200]
        }
        for hit in res["hits"]["hits"]
    ]
