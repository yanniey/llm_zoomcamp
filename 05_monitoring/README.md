## Week 5: Monitoring
* Build a streamlit app to:
    * Chat with LLM - `make chat` 
    * Visualise the data we're collecting - `make dashboard`
* Use python to create a PostgreDB and the logs in a Postgres DB, which is then fed to Grafana
* Collect user feedbacks 
* See `Makefile` for shortcuts


#### Setup

Run this in terminal: 
```
PREFIX="https://raw.githubusercontent.com/DataTalksClub/llm-zoomcamp/main"

wget ${PREFIX}/01-agentic-rag/code/ingest.py
wget ${PREFIX}/01-agentic-rag/code/rag_helper.py
```

Add dependencies:
```
uv add python-dotenv streamlit "psycopg[binary]"
```

Create a docker network for postgreDB and Grafana:
```
make network
```
Start PostgreSQL with a volume for data persistence and connect it to the network:
```
make postgres
```

SQL to create the table: make sure that postgre is running in docker before doing this. 
```
uv run python db_init.py
```

check the data in `LLMCallRecords`:
```
docker exec -it course-assistant-pg psql -U user -d course_assistant \
    -c "SELECT id, question, response_time, cost FROM LLMCallRecords;"
```

do the same & check the data using python:
```
uv run python db_query.py
```
