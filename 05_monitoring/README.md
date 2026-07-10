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
docker network create monitoring
```
Start PostgreSQL with a volume for data persistence and connect it to the network:
```
docker run -it \
    --name course-assistant-pg \
    --network monitoring \
    -e POSTGRES_USER=user \
    -e POSTGRES_PASSWORD=password \
    -e POSTGRES_DB=course_assistant \
    -p 5432:5432 \
    -v pgdata:/var/lib/postgresql/data \
    postgres:17
```

SQL to create the table:

```

```
* Use `Makefile` to set up shortcuts