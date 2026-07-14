"""Starter code for the monitoring homework.

Sets up the text-search RAG from homework 1 and a shared OpenAI client.
"""

from dotenv import load_dotenv
from gitsource import GithubRepositoryDataReader
from minsearch import Index
from openai import OpenAI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from rag_helper import RAGBase

load_dotenv()

# set up OpenTelemetry
provider = TracerProvider()  # creates the SDK's central configuration object. It owns the span processors and decides how spans are built.
provider.add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)  # wires a processor that forwards every finished span to the console exporter, one at a time. "Simple" means synchronous and immediate
trace.set_tracer_provider(
    provider
)  # registers the provider globally, so every call to trace.get_tracer(...) returns a tracer backed by it.

tracer = trace.get_tracer(
    "llm-zoomcamp"
)  # returns a Tracer we use to create spans. The string is just a label for the instrumentation scope - it identifies which part of the code produced the spans.


COMMIT = "8c1834d"

# --- Load the course lessons (same as HW1, HW2, HW4) ---
reader = GithubRepositoryDataReader(
    repo_owner="DataTalksClub",
    repo_name="llm-zoomcamp",
    commit_id=COMMIT,
    allowed_extensions={"md"},
    filename_filter=lambda path: "/lessons/" in path,
)
documents = [file.parse() for file in reader.read()]

index = Index(text_fields=["content"], keyword_fields=["filename"])
index.fit(documents)

client = OpenAI()


class RAGTraced(RAGBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, model="gpt-5.4-nano")

    def llm(self, prompt):
        with tracer.start_as_current_span("llm") as span:
            response = super().llm(prompt)
            span.set_attribute("llm_response", response.output_text)
            span.set_attribute("input_tokens", response.usage.input_tokens)
            span.set_attribute("output_tokens", response.usage.output_tokens)
        return response

    def search(self, query):
        with tracer.start_as_current_span("search") as span:
            search_results = super().search(query)
            span.set_attribute("num of docs retrieved", len(search_results))
        return search_results

    def rag(self, query):
        with tracer.start_as_current_span("rag") as span:
            search_results = self.search(query)
            prompt = self.build_prompt(query, search_results)
            answer = self.llm(prompt)
            span.set_attribute("answer", answer.output_text)
        return answer.output_text


rag = RAGTraced(index=index, llm_client=client)


if __name__ == "__main__":
    query = "How does the agentic loop keep calling the model until it stops?"
    answer = rag.rag(query)
    print(answer)
