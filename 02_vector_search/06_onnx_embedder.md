# ONNX Runtime instead of PyTorch for embeddings

When moving to production, `sentence-transformers` drags in PyTorch plus a pile of Nvidia libraries. ONNX Runtime serves the same model without that weight.

I compared two empty projects to put a number on it:

- `uv add sentence-transformers`: 4.8 GB, 58 packages
- ONNX Runtime setup: 147 MB, 27 packages

33x smaller, same embeddings, same results.

## Project setup

I created a separate project for this:

```bash
mkdir llm-zoomcamp-onnx && cd llm-zoomcamp-onnx
uv init --no-workspace
uv add onnxruntime tokenizers numpy tqdm minsearch
uv add --dev huggingface-hub jupyter
```

`huggingface-hub` is only needed to download the model. At runtime the only dependencies are `onnxruntime`, `tokenizers`, and `numpy`.

```bash
uv run python -m ipykernel install --user --name llm-zoomcamp-onnx --display-name "llm-zoomcamp-onnx"
```

## Downloading the model

I used [download.py](../embed/download.py) from `embed/` to fetch the ONNX model from HuggingFace:

```bash
uv run python download.py
```

This creates:

```text
models/
  Xenova/
    all-MiniLM-L6-v2/
      tokenizer.json
      model.onnx
```

Added `models/` to `.gitignore` — no need to commit those.

## The Embedder class

[embedder.py](../embed/embedder.py) does four things internally:

1. Tokenize — convert text into integer IDs and attention masks
2. Run ONNX model — execute the model graph on CPU
3. Mean pooling — average token embeddings weighted by attention mask
4. Normalize — divide by L2 norm so vectors can be compared with dot product

It exposes the same `encode` interface as `sentence-transformers`.

## Verifying the results match

I ran the same similarity comparison from earlier to confirm the numbers are identical:

```python
from embedder import Embedder

embed = Embedder()

q1 = "Can I still join the course after the start date?"
q2 = "How to install Docker on Windows?"
d  = "You don't need to register. You're accepted. You can also just start learning and submitting homework without registering."

v1 = embed.encode(q1)
v2 = embed.encode(q2)
dv = embed.encode(d)

v1.dot(dv)  # higher — course join query is more similar to the registration doc
v2.dot(dv)  # lower
```

Then embedded the full FAQ dataset in batches:

```python
from ingest import load_faq_data
from tqdm.auto import tqdm
import numpy as np

documents = load_faq_data()
texts = [doc["question"] + " " + doc["answer"] for doc in documents]

batch_size = 50
X = []

for i in tqdm(range(0, len(texts), batch_size)):
    batch = texts[i:i + batch_size]
    X.extend(embed.encode_batch(batch))

X = np.array(X)
```

Search works the same way:

```python
query = "Can I still join the course after the start date?"
v_query = embed.encode(query)

scores = X.dot(v_query)
documents[np.argmax(scores)]
```

Same results, 33x lighter.

## Other models

All of these work by changing the model name in `download.py` and the path in `Embedder()`:

- [Xenova/all-MiniLM-L6-v2](https://huggingface.co/Xenova/all-MiniLM-L6-v2) (384d) — small, general-purpose
- [Xenova/all-MiniLM-L12-v2](https://huggingface.co/Xenova/all-MiniLM-L12-v2) (384d) — better quality, slower
- [Xenova/paraphrase-MiniLM-L6-v2](https://huggingface.co/Xenova/paraphrase-MiniLM-L6-v2) (384d) — paraphrase detection
- [Xenova/paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/Xenova/paraphrase-multilingual-MiniLM-L12-v2) (384d) — multilingual
- [Xenova/multilingual-e5-small](https://huggingface.co/Xenova/multilingual-e5-small) (384d) — multilingual retrieval
- [Xenova/multilingual-e5-base](https://huggingface.co/Xenova/multilingual-e5-base) (768d) — stronger multilingual
- [Xenova/bge-small-en-v1.5](https://huggingface.co/Xenova/bge-small-en-v1.5) (384d) — strong retrieval
- [Xenova/bge-base-en-v1.5](https://huggingface.co/Xenova/bge-base-en-v1.5) (768d) — stronger retrieval
- [Xenova/gte-small](https://huggingface.co/Xenova/gte-small) (384d) — lightweight modern model
- [Xenova/gte-base](https://huggingface.co/Xenova/gte-base) (768d) — stronger GTE

```python
embed = Embedder("models/Xenova/bge-base-en-v1.5")
vectors = embed.encode("your text here")
print(vectors.shape)
```

Since the only runtime deps are `onnxruntime`, `tokenizers`, and `numpy`, this deploys cleanly in minimal environments — small Docker images, serverless functions, edge devices.
