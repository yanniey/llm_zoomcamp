## Week 5: Monitoring
* Build a streamlit app
* Use python to create a PostgreDB and Store the LLM logs in a SQL DB

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

SQL to create the table:

make sure that postgre is running in docker before doing this. 
```
uv run python db_init.py
```

check the data:
```
docker exec -it course-assistant-pg psql -U user -d course_assistant \
    -c "SELECT id, question, response_time, cost FROM LLMCallRecords;"
```
* Use `Makefile` to set up shortcuts