## Week 5 Homework: Monitoring
* Use [OpenTelemetry](https://opentelemetry.io/) to instrument our
RAG with traces, capture metrics as span attributes, persist the
spans to SQLite, and build a dashboard from the trace data.
* Save the OpenTelemetry span logs to SQLite DB


## Setup

Create a fresh project:

```bash
uv init
uv add gitsource minsearch openai python-dotenv opentelemetry-api opentelemetry-sdk
```

Download the starter pack:
```bash
PREFIX=https://raw.githubusercontent.com/DataTalksClub/llm-zoomcamp/main/cohorts/2026/05-monitoring
wget $PREFIX/rag_helper.py
wget $PREFIX/starter.py
```


The starter loads the 72 course lessons, builds a text-search index,
and wraps it in a `RAGBase` instance you can call right away:

```python
from starter import rag

query = "How does the agentic loop keep calling the model until it stops?"
answer = rag.rag(query)
print(answer)
```



## Q1. First trace

Wrap the `rag()` method so each call produces a span. The simplest way
is to create a `RAGTraced` subclass of `RAGBase` that wraps `rag()`,
`search()`, and `llm()` each in their own span.

Run this query:

> How does the agentic loop keep calling the model until it stops?

The console exporter prints every finished span as a dictionary.
Count the spans in the console output - each one is a separate
`ReadableSpan` entry. How many spans does the trace produce?

* [] 1
* [x] 3 - 1 for each: `search`, `llm` and `rag`
* [] 5
* [] 7

## Q2. Capturing metrics as span attributes

Spans are not just timing markers - you can attach any information you
want to them with `set_attribute`. We already use spans to record how
long each step takes. Now we'll add the metrics we care about: tokens
and cost.

Read the token usage from the LLM response (the `llm()` method in the
starter already returns the raw response object) and set them as
attributes on the `llm` span:

```python
span.set_attribute("input_tokens", usage.input_tokens)
span.set_attribute("output_tokens", usage.output_tokens)
```

And since we know both input and output tokens, we can also compute
the cost using the code from the previous modules.

Now re-run the query. How many input tokens do we see?

* [] 700
* [x] 7000
* [] 70000
* [] 700000

## Q3. Span timing

Each span automatically records its duration. Look at the console output
from Q1 and find the durations for the `search` span and the `llm` span.

For a typical query, roughly how long does the LLM call take?

* [] Under 100ms
* [] 100-500ms
* [] 500-2000ms
* [x] Over 2000ms

> The first call can be slower (cold start). Pick the range you see
> most often.