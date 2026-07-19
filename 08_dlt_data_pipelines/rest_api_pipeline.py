"""dlt REST API pipeline: load Claude Code agent trace logs from a hosted API into DuckDB."""

from typing import Any

import dlt
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


def load_logs() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="agent_traces_pipeline",
        destination="duckdb",
        dataset_name="agent_traces",
        dev_mode=True,  # fresh dataset on every run during debugging
        progress="log",
    )

    source = agent_traces_source()
    # Keep the nested "message" object as raw JSON instead of exploding it into
    # child tables -- its shape varies a lot by log type (user/assistant/tool_result).
    source.resources["logs"].apply_hints(columns={"message": {"data_type": "json"}})
    source.resources["logs"].add_limit(1)  # load a single page only for the first test run

    load_info = pipeline.run(source)
    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


if __name__ == "__main__":
    load_logs()
