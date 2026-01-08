Judge is finally live: https://esther-t.github.io/prompt-analyzer-app/

This project is a personal LLM security application designed to detect and classify potentially malicious prompts submitted to large language models.
The system analyzes user input and categorizes prompts into one of the following classes:

-SAFE -> Benign, non-malicious prompts
-SUSPICIOUS -> Prompts that may indicate misuse or risky intent
-JAILBREAK -> Prompts attempting to bypass model safeguards

The application follows a Retrieval-Augmented Generation (RAG) architecture:

a) Prompt Embedding: User prompts are converted into vector embeddings

b) Pattern Retrieval These embeddings are compared against a curated dictionary of known security and jailbreak patterns (source obtained from research articles published in top conferences).

c) LLM Evaluation: Retrieved context is then evaluated by Gemini AI, accessed via the OpenRouter.ai API, to determine the final classification.

Frontend: Hosted on GitHub Pages

Backend: Deployed on Render

Note: This project uses free-tier resources for hosting and API access.
As a result:
-The backend server may enter a sleep state when idle and can take a short time to respond on first request.
-The number of prompt evaluations per day is limited.

This project was built for learning and experimentation with:

-LLM security and prompt injection detection
-Embeddings and similarity search
-RAG-based architectures
-Third-party LLM API integrations
