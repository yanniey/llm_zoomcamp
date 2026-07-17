## Five techniques to improve retrieval quality

1. Small-to-big chunk retrieval - use small chunks for indexing but retrieve surrounding context (e.g. parent-child document retrieval (LangChain's ParentDocumentRetriever), sentence-window retrieval) for the LLM

2. Leveraging document metadata - use titles, topics, dates, and
   other metadata to filter and boost results

3. Hybrid search - combine vector search (semantic) with keyword search  in one query

4. User query rewriting - use an LLM to reformulate the user's question into a more structured query

5. Document reranking - re-order retrieved documents by relevance after the initial search, because documents with the highest embedding similarity may not be the most relevant
    * Relevance scores:
        * NDCG
        * MAP@k
        * Reciprocal Rank Fusion (RRF)
            * 
            ```text
            RRF(d) = sum(1 / (k + rank(d))) for each ranking
            ```

#### Setup
```
uv add langchain langchain-elasticsearch langchain-huggingface
```