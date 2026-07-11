run:
	uv run python assistant.py

chat:
	uv run streamlit run app.py

network: 
    # skips network creation if network already exists
	docker network inspect monitoring >/dev/null 2>&1 || docker network create monitoring

postgres: network
    # force-removes any stale course-assistant-pg container before starting a new one (the data is safe since it lives in the pgdata named volume, not the container 
	docker rm -f course-assistant-pg >/dev/null 2>&1 || true
	docker run -it \
		--name course-assistant-pg \
		--network monitoring \
		-e POSTGRES_USER=user \
		-e POSTGRES_PASSWORD=password \
		-e POSTGRES_DB=course_assistant \
		-p 5432:5432 \
		-v pgdata:/var/lib/postgresql/data \
		postgres:17
query:
	uv run python db_query.py

dashboard:
	uv run streamlit run dashboard.py --server.port 8502