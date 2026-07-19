import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Week1: RAG POC notebook where everything is written in raw python (no function wrapping), for tutorial purpose only
    """)
    return


@app.cell
def _():
    from dotenv import load_dotenv

    load_dotenv()  # if it says true then it means that it's successfully loaded the .env file
    return


@app.cell
def _():
    from openai import OpenAI

    openai_client = OpenAI()
    return (openai_client,)


@app.cell
def _(openai_client):
    def llm(prompt):
        response = openai_client.responses.create(model="gpt-5.4-mini", input=prompt)
        return response.output_text

    return (llm,)


@app.cell
def _(llm):
    llm("capital of cabo verde")
    return


@app.cell
def _():
    context = """
    I just discovered the course. Can I still join?
    Yes, but if you want to receive a certificate, you need to submit your project while we're still accepting submissions.

    Course: I have registered for the LLM Zoomcamp. When can I expect to receive the confirmation email?
    You don't need it. You're accepted. You can also just start learning and submitting homework (while the form is open) without registering. It is not checked against any registered list. Registration is just to gauge interest before the start date.

    What is the video/zoom link to the stream for the "Office Hours" or live/workshop sessions?
    The zoom link is only published to instructors/presenters/TAs. Students participate via YouTube Live and submit questions to Slido.

    Cloud alternatives with GPU
    Check the quota and reset cycle carefully. Potential options include Google Colab, Kaggle, Databricks.
    """
    return (context,)


@app.cell
def _(llm):
    question = 'I just discovered the course. Can I join now?'
    _answer = llm(question)
    print(_answer)
    return (question,)


@app.cell
def _(context, question):
    prompt = f"""
    Your task is to answer questions from the course participants
    based on the provided context.

    Use the context to find relevant information and provide accurate
    answers. If the answer is not found in the context,
    respond with "I don't know."

    Question:
    {question}

    Context:
    {context}
    """
    return (prompt,)


@app.cell
def _(llm, prompt):
    _answer = llm(prompt)
    print(_answer)
    return


@app.cell
def _():
    import requests

    docs_url = "https://datatalks.club/faq/json/courses.json"
    response = requests.get(docs_url)
    courses_raw = response.json()
    return courses_raw, requests


@app.cell
def _(courses_raw, requests):
    # fetch all docs

    documents = []
    url_prefix = "https://datatalks.club/faq"

    for course in courses_raw:
        course_url = f"""{url_prefix}{course["path"]}"""

        course_response = requests.get(course_url)
        course_response.raise_for_status()  # if something is broken, exit
        course_data = course_response.json()

        documents.extend(course_data)

    len(documents)
    return (documents,)


@app.cell
def _(documents):
    documents[500]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Search

    Indexing with minsearch
    """)
    return


@app.cell
def _():
    from minsearch import Index

    return (Index,)


@app.cell
def _(Index, documents):
    index = Index(text_fields=["question", "section", "answer"], keyword_fields=["course"])

    index.fit(documents)
    return (index,)


@app.cell
def _(index):
    def search(question, course="llm-zoomcamp"):
        boost_dict = {
            "question": 2.0,
            "section": 0.5,
        }  # if a field is more important to search, then boost its relevancy in search results
        filter_dict = {"course": course}

        return index.search(
            question, boost_dict=boost_dict, filter_dict=filter_dict, num_results=5
        )

    return (search,)


@app.cell
def _(index, question):
    search_results = index.search(
        question,
        filter_dict={"course": "llm-zoomcamp"},
        boost_dict={"question": 2.0, "section": 1.0, "answer": 1.0},
        num_results=5,
    )

    search_results
    return (search_results,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Prompt
    """)
    return


@app.cell
def _():
    INSTRUCTIONS = """
    Your task is to answer questions from the course participants
    based on the provided context.

    Use the context to find relevant information and provide accurate
    answers. If the answer is not found in the context,
    respond with "I don't know."
    """
    return (INSTRUCTIONS,)


@app.cell
def _():
    USER_PROMPT_TEMPLATE = """
    Question: 
    {question}

    Context:
    {context}
    """
    return (USER_PROMPT_TEMPLATE,)


@app.function
def build_context(search_results):
    lines = []

    for doc in search_results:
        lines.append(doc["section"])
        lines.append("Q: " + doc["question"])
        lines.append("A: " + doc["answer"])
        lines.append("")

    return "\n".join(lines).strip()


@app.cell
def _(USER_PROMPT_TEMPLATE):
    def build_prompt(question, search_results):
        context = build_context(search_results)
        prompt = USER_PROMPT_TEMPLATE.format(question=question, context=context)
        return prompt.strip()

    return (build_prompt,)


@app.cell
def _(build_prompt, question, search_results):
    prompt_1 = build_prompt(question, search_results)
    return (prompt_1,)


@app.cell
def _(openai_client, prompt_1):
    response_1 = openai_client.responses.create(model='gpt-5.4-mini', input=prompt_1)
    return (response_1,)


@app.cell
def _(response_1):
    print(response_1.model_dump_json(indent=2))
    return


@app.cell
def _(response_1):
    response_1.usage  # shows the # of input, cached & output tokens,
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Estimate cost
    """)
    return


@app.cell
def _(response_1):
    input_price = 0.75 / 1000000  # for gpt-5.4 mini
    output_price = 4.5 / 1000000
    cost = response_1.usage.input_tokens * input_price + response_1.usage.output_tokens * output_price
    cost
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Add memory
    """)
    return


@app.cell
def _(openai_client):
    def llm_1(instructions, user_prompt, model='gpt-5.4-mini'):
        message_history = [{'role': 'developer', 'content': instructions}, {'role': 'user', 'content': user_prompt}]
        response = openai_client.responses.create(model=model, input=message_history)
        return response.output_text

    return (llm_1,)


@app.cell
def _(INSTRUCTIONS, llm_1, prompt_1):
    print(llm_1(INSTRUCTIONS, prompt_1))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Full RAG
    """)
    return


@app.cell
def _(INSTRUCTIONS, build_prompt, llm_1, search):
    def rag(query, model='gpt-5.4-mini'):
        search_results = search(query)
        prompt = build_prompt(query, search_results)
        _answer = llm_1(INSTRUCTIONS, prompt, model=model)
        return _answer

    return (rag,)


@app.cell
def _(question, rag):
    _answer = rag(question)
    print(_answer)
    return


if __name__ == "__main__":
    app.run()
