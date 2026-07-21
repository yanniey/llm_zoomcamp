## Project: Build an end-to-end LLM app

[Project](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md)

* Can be a RAG app, agent app, or a combination of both
* Select a dataset or API-backed data source
* Ingest the data into a knowledge base, or connect to the API that provides the data
* Implement the application flow: retrieve context from the data, optionally call tools, build the prompt, and send it to an LLM
* Evaluate the performance of your RAG or agent flow
* Create an interface for the application
* Collect user feedback and monitor your application
* Search, evaluation, api, monitoring + docker containerisation


#### LLM-as-a judge for askmii
- [ ] Collect dataset for good question vs. answer pairs - `eval_dataset`
- [ ] Data enrichment: Create syntheic data based on good question vs. answer pairs - `enriched_eval_dataset`
- [ ] Create eval scripts against:
    - [ ] Relevance
    - [ ] Correctness/Faithfulness
- [ ] Create a streamlit app to colelct data for Human-in-the-loop review