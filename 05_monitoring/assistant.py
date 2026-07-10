import sys

from db_save import save_conversation
from dotenv import load_dotenv
from ingest import build_index, load_faq_data
from metrics import RAGWithMetrics
from openai import OpenAI


def create_assistant():
    load_dotenv()

    documents = load_faq_data()
    index = build_index(documents)

    return RAGWithMetrics(
        index=index,
        llm_client=OpenAI(),
    )


if __name__ == "__main__":
    assistant = create_assistant()

    query = "how to join this course"
    if len(sys.argv) > 1:
        query = sys.argv[1]

    answer = assistant.rag(query)
    print(answer)

    # make sure that every CLI test is saved in postgreDB
    save_conversation(assistant.last_call, query, "llm-zoomcamp")
