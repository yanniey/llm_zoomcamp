## Week 5: Monitoring

#### Setup

Run this in terminal: 
```
PREFIX="https://raw.githubusercontent.com/DataTalksClub/llm-zoomcamp/main"

wget ${PREFIX}/01-agentic-rag/code/ingest.py
wget ${PREFIX}/01-agentic-rag/code/rag_helper.py
```

Add dependencies:
```
uv add python-dotenv streamlit
```

Use `Makefile` to set up shortcuts