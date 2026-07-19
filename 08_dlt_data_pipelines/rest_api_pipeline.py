"""dlt REST API pipeline: load Claude Code agent trace logs from a hosted API into DuckDB.

Source: https://test-agent-traces-api-xt2e7ottma-ew.a.run.app (no auth)
Endpoint: GET /logs - offset/limit pagination, `total` = 1 mil rows
data lives under the `logs` key of the response.

"""

from typing import Any

import dlt
from dlt.hub import run
from dlt.hub.run import trigger
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources


@dlt.source(name="agent_traces")
def agent_traces_source(base_url: str = dlt.config.value) -> Any:
    """Load agent trace logs from the /logs endpoint.

    Args:
        base_url: API base URL. Auto-loaded from config.toml under [sources.agent_traces].
    """
    config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
        },
        "resources": [
            {
                "name": "logs",
                "primary_key": "uuid",
                "write_disposition": "replace",
                "endpoint": {
                    "path": "logs",
                    "params": {
                        "limit": 1000,
                    },
                    "paginator": {
                        "type": "offset",
                        "limit": 1000,
                        "offset_param": "offset",
                        "limit_param": "limit",
                        "total_path": "total",
                    },
                    "data_selector": "logs",
                },
            },
        ],
    }

    yield from rest_api_resources(config)


# run this as a cron job every Sunday at 12 pm
@run.pipeline("agent_traces_pipeline", trigger=trigger.schedule("0 12 * * 0"))
def load_logs(row_limit: int = 20_000) -> None:
    pipeline = dlt.pipeline(
        pipeline_name="agent_traces_pipeline",
        destination="playground",
        dataset_name="agent_traces",
    )

    source = agent_traces_source()
    # Keep the nested "message" object as raw JSON instead of exploding it into
    # child tables -- its shape varies a lot by log type (user/assistant/tool_result).
    source.resources["logs"].apply_hints(columns={"message": {"data_type": "json"}})
    source.resources["logs"].add_limit(row_limit, count_rows=True)

    load_info = pipeline.run(source)
    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


if __name__ == "__main__":
    load_logs()
