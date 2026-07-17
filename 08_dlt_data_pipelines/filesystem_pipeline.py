"""dlt filesystem pipeline: load raw Claude Code session logs (JSONL) into DuckDB."""

import json
from typing import Iterator

import dlt
from dlt.sources.filesystem import filesystem, FileItemDict
from dlt.sources import TDataItems


@dlt.transformer
def read_raw_jsonl(items: Iterator[FileItemDict]) -> Iterator[TDataItems]:
    """Yield one row per JSONL line, keeping the full parsed object as raw JSON."""
    for file_obj in items:
        with file_obj.open() as f:
            for line_number, raw_line in enumerate(f, start=1):
                if isinstance(raw_line, bytes):
                    raw_line = raw_line.decode("utf-8")
                raw_line = raw_line.strip()
                if not raw_line:
                    continue
                yield {
                    "file_name": file_obj["file_name"],
                    "line_number": line_number,
                    "data": json.loads(raw_line),
                }


def load_raw_events() -> None:
    """Load raw Claude Code session logs into DuckDB.

    bucket_url is read from .dlt/config.toml under [sources.filesystem].
    """
    pipeline = dlt.pipeline(
        pipeline_name="claude_logs_pipeline",
        destination="duckdb",
        dataset_name="claude_logs",
        dev_mode=True,  # fresh dataset on every run during dev
    )

    files = filesystem(file_glob="*.jsonl")
    reader = (files | read_raw_jsonl()).with_name("raw_events")
    reader.apply_hints(columns={"data": {"data_type": "json"}})

    load_info = pipeline.run(reader, write_disposition="replace")
    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


if __name__ == "__main__":
    load_raw_events()
