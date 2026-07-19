# use marimo to build a report on claude logs
import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    from pathlib import Path

    import altair as alt
    import marimo as mo
    import pandas as pd

    mo.md("# Claude Code Usage Report")
    return Path, alt, json, mo, pd


@app.cell
def _(mo):
    mo.md("""
    Reads local Claude Code session transcripts from `~/.claude/projects/**/*.jsonl`
    and summarizes activity: sessions, messages, tool calls, token usage, and
    estimated cost.

    **Note on cost:** pricing is looked up per model from the table below. Rates
    reflect list pricing as of 2026-07; Claude Sonnet 5 is priced at its
    introductory rate ($2/$10 per MTok) through 2026-08-31, after which it reverts
    to $3/$15. Costs here are estimates only — they do not account for
    prompt-cache write/read discounts precisely reflected below, batch pricing, or
    any other discounts on the account.
    """)
    return


@app.cell
def _(Path, json):
    CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"

    def iter_session_files():
        if not CLAUDE_PROJECTS_DIR.exists():
            return
        for project_dir in sorted(CLAUDE_PROJECTS_DIR.iterdir()):
            if not project_dir.is_dir():
                continue
            for jsonl_file in sorted(project_dir.glob("*.jsonl")):
                yield project_dir.name, jsonl_file

    def load_records():
        records = []
        for project_name, jsonl_file in iter_session_files():
            try:
                with open(jsonl_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            rec = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        rec["_project"] = project_name
                        rec["_file"] = jsonl_file.name
                        records.append(rec)
            except OSError:
                continue
        return records

    raw_records = load_records()
    len(raw_records)
    return (raw_records,)


@app.cell
def _(pd, raw_records):
    # Assistant messages carry token usage, but each content block (thinking,
    # tool_use, text) within one API call repeats the same usage totals under the
    # same requestId -- dedupe on requestId before summing to avoid overcounting.
    seen_request_ids = set()
    usage_rows = []
    tool_call_rows = []
    message_rows = []

    for rec in raw_records:
        rtype = rec.get("type")
        ts = rec.get("timestamp")
        session_id = rec.get("sessionId") or rec.get("session_id")
        project = rec.get("_project")
        cwd = rec.get("cwd")
        git_branch = rec.get("gitBranch")

        if rtype in ("user", "assistant"):
            message_rows.append({
                "timestamp": ts,
                "project": project,
                "session_id": session_id,
                "role": rtype,
                "cwd": cwd,
            })

        if rtype != "assistant":
            continue

        message = rec.get("message") or {}
        request_id = rec.get("requestId")
        model = message.get("model")

        for block in message.get("content") or []:
            if block.get("type") == "tool_use":
                tool_call_rows.append({
                    "timestamp": ts,
                    "project": project,
                    "session_id": session_id,
                    "tool_name": block.get("name"),
                })

        if request_id is None or request_id in seen_request_ids:
            continue
        seen_request_ids.add(request_id)

        usage = message.get("usage") or {}
        usage_rows.append({
            "timestamp": ts,
            "project": project,
            "session_id": session_id,
            "model": model,
            "cwd": cwd,
            "git_branch": git_branch,
            "input_tokens": usage.get("input_tokens", 0) or 0,
            "output_tokens": usage.get("output_tokens", 0) or 0,
            "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0)
            or 0,
            "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0) or 0,
        })

    usage_df = pd.DataFrame(usage_rows)
    tool_calls_df = pd.DataFrame(tool_call_rows)
    messages_df = pd.DataFrame(message_rows)

    if not usage_df.empty:
        usage_df["timestamp"] = pd.to_datetime(
            usage_df["timestamp"], utc=True, errors="coerce"
        )
        usage_df["date"] = usage_df["timestamp"].dt.date
    if not tool_calls_df.empty:
        tool_calls_df["timestamp"] = pd.to_datetime(
            tool_calls_df["timestamp"], utc=True, errors="coerce"
        )
    if not messages_df.empty:
        messages_df["timestamp"] = pd.to_datetime(
            messages_df["timestamp"], utc=True, errors="coerce"
        )
        messages_df["date"] = messages_df["timestamp"].dt.date

    len(usage_df), len(tool_calls_df), len(messages_df)
    return messages_df, tool_calls_df, usage_df


@app.cell
def _(mo):
    # $ per million tokens: (input, output). Cache writes/reads are priced
    # relative to input price (1.25x write, 0.1x read) per Anthropic's standard
    # prompt-caching economics.
    MODEL_PRICING = {
        "claude-fable-5": (10.00, 50.00),
        "claude-mythos-5": (10.00, 50.00),
        "claude-opus-4-8": (5.00, 25.00),
        "claude-opus-4-7": (5.00, 25.00),
        "claude-opus-4-6": (5.00, 25.00),
        "claude-sonnet-5": (2.00, 10.00),  # introductory rate through 2026-08-31
        "claude-sonnet-4-6": (3.00, 15.00),
        "claude-haiku-4-5": (1.00, 5.00),
    }
    DEFAULT_PRICING = (3.00, 15.00)

    mo.md(
        "Model pricing table (USD per million tokens, input/output) used for cost estimates:"
    )
    return DEFAULT_PRICING, MODEL_PRICING


@app.cell
def _(MODEL_PRICING, mo, pd):
    pricing_table = pd.DataFrame([
        {"model": m, "input_per_mtok": i, "output_per_mtok": o}
        for m, (i, o) in MODEL_PRICING.items()
    ])
    mo.ui.table(pricing_table)
    return


@app.cell
def _(DEFAULT_PRICING, MODEL_PRICING, usage_df):
    def estimate_cost(row):
        in_rate, out_rate = MODEL_PRICING.get(row["model"], DEFAULT_PRICING)
        cost = 0.0
        cost += row["input_tokens"] / 1e6 * in_rate
        cost += row["output_tokens"] / 1e6 * out_rate
        cost += row["cache_creation_input_tokens"] / 1e6 * in_rate * 1.25
        cost += row["cache_read_input_tokens"] / 1e6 * in_rate * 0.1
        return cost

    if not usage_df.empty:
        usage_df["estimated_cost_usd"] = usage_df.apply(estimate_cost, axis=1)
        usage_df["total_tokens"] = (
            usage_df["input_tokens"]
            + usage_df["output_tokens"]
            + usage_df["cache_creation_input_tokens"]
            + usage_df["cache_read_input_tokens"]
        )
    return


@app.cell
def _(mo, tool_calls_df, usage_df):
    n_sessions = usage_df["session_id"].nunique() if not usage_df.empty else 0
    n_projects = usage_df["project"].nunique() if not usage_df.empty else 0
    n_api_calls = len(usage_df)
    n_tool_calls = len(tool_calls_df)
    total_tokens = usage_df["total_tokens"].sum() if not usage_df.empty else 0
    total_cost = usage_df["estimated_cost_usd"].sum() if not usage_df.empty else 0.0

    mo.hstack(
        [
            mo.stat(value=n_sessions, label="Sessions"),
            mo.stat(value=n_projects, label="Projects"),
            mo.stat(value=n_api_calls, label="API calls"),
            mo.stat(value=n_tool_calls, label="Tool calls"),
            mo.stat(value=f"{total_tokens:,.0f}", label="Total tokens"),
            mo.stat(value=f"${total_cost:,.2f}", label="Est. cost"),
        ],
        widths="equal",
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Token usage & cost over time
    """)
    return


@app.cell
def _(alt, mo, usage_df):
    if usage_df.empty:
        daily_chart = mo.md("_No usage data found._")
    else:
        daily = (
            usage_df
            .groupby("date")
            .agg(
                total_tokens=("total_tokens", "sum"),
                estimated_cost_usd=("estimated_cost_usd", "sum"),
                api_calls=("model", "count"),
            )
            .reset_index()
        )
        daily["date"] = daily["date"].astype(str)

        tokens_chart = (
            alt
            .Chart(daily)
            .mark_bar()
            .encode(
                x=alt.X("date:O", title="Date"),
                y=alt.Y("total_tokens:Q", title="Total tokens"),
                tooltip=["date", "total_tokens", "api_calls"],
            )
            .properties(width=700, height=250, title="Tokens per day")
        )
        cost_chart = (
            alt
            .Chart(daily)
            .mark_bar(color="#c1666b")
            .encode(
                x=alt.X("date:O", title="Date"),
                y=alt.Y("estimated_cost_usd:Q", title="Estimated cost (USD)"),
                tooltip=["date", "estimated_cost_usd"],
            )
            .properties(width=700, height=250, title="Estimated cost per day")
        )
        daily_chart = mo.vstack([
            mo.ui.altair_chart(tokens_chart),
            mo.ui.altair_chart(cost_chart),
        ])

    daily_chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Usage by project
    """)
    return


@app.cell
def _(alt, mo, usage_df):
    if usage_df.empty:
        by_project_chart = mo.md("_No usage data found._")
    else:
        by_project = (
            usage_df
            .groupby("project")
            .agg(
                total_tokens=("total_tokens", "sum"),
                estimated_cost_usd=("estimated_cost_usd", "sum"),
                sessions=("session_id", "nunique"),
                api_calls=("model", "count"),
            )
            .reset_index()
            .sort_values("total_tokens", ascending=False)
        )

        by_project_chart = mo.vstack([
            mo.ui.table(by_project),
            mo.ui.altair_chart(
                alt
                .Chart(by_project)
                .mark_bar()
                .encode(
                    x=alt.X("total_tokens:Q", title="Total tokens"),
                    y=alt.Y("project:N", sort="-x", title="Project"),
                    tooltip=[
                        "project",
                        "total_tokens",
                        "estimated_cost_usd",
                        "sessions",
                    ],
                )
                .properties(width=700, height=150, title="Tokens by project")
            ),
        ])

    by_project_chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Usage by model
    """)
    return


@app.cell
def _(alt, mo, usage_df):
    if usage_df.empty:
        by_model_chart = mo.md("_No usage data found._")
    else:
        by_model = (
            usage_df
            .groupby("model")
            .agg(
                total_tokens=("total_tokens", "sum"),
                estimated_cost_usd=("estimated_cost_usd", "sum"),
                api_calls=("model", "count"),
            )
            .reset_index()
            .sort_values("estimated_cost_usd", ascending=False)
        )

        by_model_chart = mo.vstack([
            mo.ui.table(by_model),
            mo.ui.altair_chart(
                alt
                .Chart(by_model)
                .mark_arc()
                .encode(
                    theta=alt.Theta("estimated_cost_usd:Q"),
                    color=alt.Color("model:N"),
                    tooltip=["model", "estimated_cost_usd", "total_tokens"],
                )
                .properties(
                    width=400, height=300, title="Estimated cost share by model"
                )
            ),
        ])

    by_model_chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Most-used tools
    """)
    return


@app.cell
def _(alt, mo, tool_calls_df):
    if tool_calls_df.empty:
        tool_chart = mo.md("_No tool call data found._")
    else:
        tool_counts = (
            tool_calls_df
            .groupby("tool_name")
            .size()
            .reset_index(name="calls")
            .sort_values("calls", ascending=False)
        )

        tool_chart = mo.ui.altair_chart(
            alt
            .Chart(tool_counts.head(20))
            .mark_bar()
            .encode(
                x=alt.X("calls:Q", title="Calls"),
                y=alt.Y("tool_name:N", sort="-x", title="Tool"),
                tooltip=["tool_name", "calls"],
            )
            .properties(width=700, height=400, title="Tool call frequency (top 20)")
        )

    tool_chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Sessions over time
    """)
    return


@app.cell
def _(alt, messages_df, mo):
    if messages_df.empty:
        sessions_chart = mo.md("_No message data found._")
    else:
        sessions_per_day = (
            messages_df
            .dropna(subset=["date"])
            .groupby("date")["session_id"]
            .nunique()
            .reset_index(name="active_sessions")
        )
        sessions_per_day["date"] = sessions_per_day["date"].astype(str)

        messages_per_day = (
            messages_df
            .dropna(subset=["date"])
            .groupby(["date", "role"])
            .size()
            .reset_index(name="messages")
        )
        messages_per_day["date"] = messages_per_day["date"].astype(str)

        sessions_chart = mo.vstack([
            mo.ui.altair_chart(
                alt
                .Chart(sessions_per_day)
                .mark_line(point=True)
                .encode(
                    x=alt.X("date:O", title="Date"),
                    y=alt.Y("active_sessions:Q", title="Active sessions"),
                    tooltip=["date", "active_sessions"],
                )
                .properties(width=700, height=250, title="Active sessions per day")
            ),
            mo.ui.altair_chart(
                alt
                .Chart(messages_per_day)
                .mark_bar()
                .encode(
                    x=alt.X("date:O", title="Date"),
                    y=alt.Y("messages:Q", title="Messages"),
                    color=alt.Color("role:N"),
                    tooltip=["date", "role", "messages"],
                )
                .properties(width=700, height=250, title="Messages per day by role")
            ),
        ])

    sessions_chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Raw usage data
    """)
    return


@app.cell
def _(mo, usage_df):
    mo.ui.table(
        usage_df.sort_values("timestamp", ascending=False)
    ) if not usage_df.empty else mo.md("_No usage data found._")
    return


if __name__ == "__main__":
    app.run()
