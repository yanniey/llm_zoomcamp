# llm_zoomcamp
2026 cohort of the [LLM Zoomcamp ran by DataTalksClub](https://github.com/DataTalksClub/llm-zoomcamp/tree/main)

## Week 1: 
* RAG
* persistent knowledge base (`sqlite`) & indexing 
* agentic RAG
    * function calling
    * agentic loops
    * frameworks for running agentic loops 

### Week 1 Notebooks 
* `01_rag_poc.ipynb`: RAG tutorial notebook where everything is written as it is
* `02_rag_cleaned.ipynb`: RAG POC notebook where the functions are split out, e.g. `ingest.py` 
* `03_persistent_rag_ingestion.ipynb`: Replaces in-memory knowledge base (KB) with persistent KB (sqlite)
* `04_rag_cleaned_with_persistent_knowledge_base.ipynb`: RAG POC notebook that uses persistent KB index

## Week 2: 
* vector search, pgvector
* using `sentence_transformers` and `onnx` models

## Week 3:
* Workflow orchestration with Kestra

## Week 4:
* Evaluation: 
  * Search eval: does the search return the right docs?
    * Metrics: 
      - 1. Hit Rate
      - 2. MRR (Mean Reciprocal Rank)
  * RAG eval: does the LLM generate good answers?
    * Metric: LLM-as-a-judge
  * Agent eval: does the agent user tools efficiently?
    * Metrics:
      - 1. Final answer
      - 2. tool-recall trajectory

## Setup 
```
pip install uv
uv sync 
```


## Homeworks 
* [Answer to Homeworks](https://courses.datatalks.club/llm-zoomcamp-2026/)