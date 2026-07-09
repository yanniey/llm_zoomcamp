# llm_zoomcamp
2026 cohort of the [LLM Zoomcamp ran by DataTalksClub](https://github.com/DataTalksClub/llm-zoomcamp/tree/main)

## Week 1: Agentic RAG
* persistent knowledge base (`sqlite`) & indexing 
* agentic RAG
    * function calling
    * agentic loops
    * frameworks for running agentic loops 

## Week 2: * vector search with `pgvector`
* using `sentence_transformers` and `onnx` models

## Week 3: Workflow orchestration with Kestra

## Week 4: Evaluation
* Search eval: does the search return the right docs?
  - 1. Hit Rate
  - 2. MRR (Mean Reciprocal Rank)
* RAG eval: does the LLM generate good answers?
  * LLM-as-a-judge
* Agent eval: does the agent user tools efficiently?
  - 1. Final answer
  - 2. tool-recall trajectory

## Week 5: Monitoring
* 

## Setup 
```
pip install uv
uv sync 
```

## Homeworks 
* [Answer to Homeworks](https://courses.datatalks.club/llm-zoomcamp-2026/)



TODO
1. create ground data for askmii for search eval (week 4)
2. create a dataset of docs retrieved for a convo in askmii
3. implement LLM-as-a-judge for Askmii