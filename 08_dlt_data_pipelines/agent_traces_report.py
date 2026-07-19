# use marimo to build a report on claude logs from mimic Anthropic API.
# Source: https://test-agent-traces-api-xt2e7ottma-ew.a.run.app

import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import altair as alt
    import dlt
    import marimo as mo

    mo.md("# Agent Traces Report")
    return alt, dlt, mo


@app.cell
def _(mo):
    mo.md("""
    Reads agent trace logs loaded by `rest_api_pipeline.py` (`agent_traces_pipeline`)
    from the fake Anthropic-mimicking API, and summarizes activity, log types,
    token usage, and models used.
    """)
    return


@app.cell
def _(dlt):
    pipeline = dlt.attach(
        "agent_traces_pipeline",
        destination="playground",
        dataset_name="agent_traces",
        # playground is a managed S3 service by dlthub
    )
    dataset = pipeline.dataset()
    return (dataset,)


@app.cell
def _(mo):
    mo.md("""
    ## Activity Over Time
    """)
    return


@app.cell
def _(dataset):
    df_chart1 = dataset("""
        SELECT
            time_bucket(INTERVAL 10 MINUTE, timestamp) AS bucket,
            type,
            count(*) AS cnt
        FROM logs
        GROUP BY 1, 2
        ORDER BY 1
    """).df()
    return (df_chart1,)


@app.cell
def _(alt, df_chart1):
    _chart = (
        alt
        .Chart(df_chart1)
        .mark_line(point=True)
        .encode(
            x=alt.X("bucket:T", title="Time"),
            y=alt.Y("cnt:Q", title="Log entries"),
            color=alt.Color("type:N", title="Type"),
            tooltip=["bucket:T", "type:N", "cnt:Q"],
        )
        .properties(title="Activity Over Time (10-min buckets)")
    )
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Log Type Breakdown
    """)
    return


@app.cell
def _(dataset):
    df_chart2 = dataset("""
        SELECT
            type,
            count(*) AS cnt
        FROM logs
        GROUP BY 1
        ORDER BY 2 DESC
    """).df()
    return (df_chart2,)


@app.cell
def _(alt, df_chart2):
    _chart = (
        alt
        .Chart(df_chart2)
        .mark_bar()
        .encode(
            x=alt.X("type:N", title="Type", sort="-y"),
            y=alt.Y("cnt:Q", title="Log entries"),
            tooltip=["type:N", "cnt:Q"],
        )
        .properties(title="Log Entries by Type")
    )
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Token Usage Over Time
    """)
    return


@app.cell
def _(dataset):
    df_chart3 = dataset("""
        SELECT
            time_bucket(INTERVAL 10 MINUTE, timestamp) AS bucket,
            sum(usage__input_tokens) AS input_tokens,
            sum(usage__output_tokens) AS output_tokens
        FROM logs
        WHERE type = 'assistant'
        GROUP BY 1
        ORDER BY 1
    """).df()
    return (df_chart3,)


@app.cell
def _(alt, df_chart3):
    df_chart3_long = df_chart3.melt(
        id_vars=["bucket"],
        value_vars=["input_tokens", "output_tokens"],
        var_name="token_type",
        value_name="tokens",
    )
    _chart = (
        alt
        .Chart(df_chart3_long)
        .mark_line(point=True)
        .encode(
            x=alt.X("bucket:T", title="Time"),
            y=alt.Y("tokens:Q", title="Tokens"),
            color=alt.Color("token_type:N", title="Token type"),
            tooltip=["bucket:T", "token_type:N", "tokens:Q"],
        )
        .properties(title="Token Usage Over Time")
    )
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Models Used
    """)
    return


@app.cell
def _(dataset):
    df_chart4 = dataset("""
        SELECT
            json_extract_string(message, '$.model') AS model,
            count(*) AS cnt
        FROM logs
        WHERE type = 'assistant'
        GROUP BY 1
        ORDER BY 2 DESC
    """).df()
    return (df_chart4,)


@app.cell
def _(alt, df_chart4):
    _chart = (
        alt
        .Chart(df_chart4)
        .mark_bar()
        .encode(
            x=alt.X("model:N", title="Model", sort="-y"),
            y=alt.Y("cnt:Q", title="Assistant messages"),
            tooltip=["model:N", "cnt:Q"],
        )
        .properties(title="Assistant Messages by Model")
    )
    _chart
    return


if __name__ == "__main__":
    app.run()
