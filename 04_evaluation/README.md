## Week 4 - Evaluations

* Create synthetic ground truth data with LLM (`01_data_gen.ipynb`)
    * Use structured outputs (openai.responses.parse(), which is openai.responses.create() + auto JSON schema injection + deserialisation)
    * Parallel processing for synthetic data generation
* Search eval with `hit rate` and `mean reciprocal rank`, using grid search
* LLM-as-a-judge & tool-call trajectories

* Use a bigger, more competent LLM model for eval than generation. The evaluator needs to be more capable than generator. 
* Bigger models should be used for 
  * 1) agentic reasoning 
  * 2) eval 

#### The evaluation workflow in practice

1. Start with synthetic data. Use an LLM to generate questions from
   your FAQ or documentation. This gives you a baseline without needing
   real users.
2. Tune the data generation. If the metrics look suspiciously good,
   the synthetic questions may be too close to the source text. Adjust
   the generation prompt to produce more realistic questions.
3. Deploy and collect real data. Once the system is in production, start
   collecting actual user queries and feedback.
4. Label real data. Have humans label whether the retrieved documents
   and generated answers are correct. This produces the most reliable
   ground truth.
5. Tune synthetic generation to match real data. Use the patterns from
   real queries to improve your synthetic data generator. The closer
   your synthetic data is to real data, the more useful the metrics
   become.

Nothing beats manual evaluation. Try the system yourself, think about
edge cases, and collect examples of where it fails. This is especially
important in the early stages when you don't have automated evaluation
set up yet.


#### Popular eval frameworks
* `DeepEval`: we use this at Utility Warehouse. Provides built-in metrics for RAG evaluation including hallucination detection and answer relevance
* `Ragas`: a framework for evaluating RAG systems with metrics like faithfulness, answer relevance, and context precision
* `TruLens`: instruments your LLM app and tracks quality metrics
