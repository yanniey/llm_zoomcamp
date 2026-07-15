## Five techniques to improve retrieval quality

1. Small-to-big chunk retrieval - use small chunks for indexing
   but retrieve surrounding context for the LLM
2. Leveraging document metadata - use titles, topics, dates, and
   other metadata to filter and boost results
3. Hybrid search - combine vector search (semantic) with keyword
   search (lexical) in one query
4. User query rewriting - use an LLM to reformulate the user's
   question into a better search query
5. Document reranking - re-order retrieved documents by relevance
   after the initial search