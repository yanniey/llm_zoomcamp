## Hybrid Search with Langchain

* Rewrite the hybrid search using LangChain's `ElasticsearchRetriever`

## Setting up the retriever

LangChain provides `ElasticsearchRetriever`, a wrapper around the Elasticsearch client.

We configure it with a hybrid query function:

```python
from langchain_huggingface import HuggingFaceEmbeddings
from typing import Dict
from langchain_elasticsearch import ElasticsearchRetriever

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
)

es_url = "http://localhost:9200"


def hybrid_query(search_query: str) -> Dict:
    """
    A hybrid search function that combines keyword and vector search:
    """
    vector = embedding.embed_query(search_query)
    return {
        # text search
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": search_query,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields",
                    }
                },
                "filter": {"term": {"course": "llm-zoomcamp"}},
            }
        },
        # vector search
        "knn": {
            "field": "question_text_vector",
            "query_vector": vector,
            "k": 5,
            "num_candidates": 10000,
        },
        "size": 5,
    }


# Create the retriever from the query function
hybrid_retriever = ElasticsearchRetriever.from_es_params(
    url=es_url,
    index_name="course-questions",
    body_func=hybrid_query,
    content_field="text",
)

# do the search
query = "I just discovered the course. Can I still join it?"
results = hybrid_retriever.invoke(query)

for result in results:
    print(result.metadata["_source"]["question"])
    print(result.metadata["_score"])
```

## Evaluating with LangChain

```python
def elastic_search_hybrid(field, query, course):
    """
    wrap the retriever in a function that works with the ground truth data
    """

    def hybrid_query(search_query: str) -> Dict:
        vector = embedding.embed_query(search_query)
        return {
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": search_query,
                            "fields": ["question^3", "text", "section"],
                            "type": "best_fields",
                        }
                    },
                    "filter": {"term": {"course": course}},
                }
            },
            "knn": {
                "field": field,
                "query_vector": vector,
                "k": 5,
                "num_candidates": 10000,
            },
            "size": 5,
        }

    retriever = ElasticsearchRetriever.from_es_params(
        url=es_url,
        index_name="course-questions",
        body_func=hybrid_query,
        content_field="text",
    )

    # Run the retriever and format the results
    results = retriever.invoke(query)
    return [
        {
            "id": r.metadata["_source"]["id"],
            "question": r.metadata["_source"]["question"],
            "text": r.metadata["_source"]["text"],
        }
        for r in results
    ]


def question_text_hybrid(q):
    return elastic_search_hybrid("question_text_vector", q["question"], q["course"])


evaluate(ground_truth, question_text_hybrid)
```

The results match what we got with direct Elasticsearch queries: Hit Rate 0.925 and MRR 0.851.