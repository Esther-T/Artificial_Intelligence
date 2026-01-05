from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np
from gpt4all import GPT4All

MODEL_NAME = "\\AI\\Models\\Meta-Llama-3.1-8B-Instruct-Q8_0.gguf"
gptModel = GPT4All(MODEL_NAME)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

docs = json.load(open("\\AI\\Agents\\jailbreak.json"))
texts = [d["text"] for d in docs]

embeddings = model.encode(texts, normalize_embeddings=True)

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(np.array(embeddings))

faiss.write_index(index, "jailbreak.index")


def retrieve_jailbreak_context(user_input, k=3):
    query_emb = model.encode([user_input], normalize_embeddings=True)
    D, I = index.search(query_emb, k)

    return [docs[i] for i in I[0]]
    
def detect_intent(user_input: str) -> str:
    retrieved = retrieve_jailbreak_context(user_input, k=3)
    
    patterns_text = "\n".join(f"- {item['text']}" for item in retrieved)
         
    classifier_prompt = f"""
    
    You are a classifier.

    Output exactly one label:
    SAFE
    SUSPICIOUS
    JAILBREAK

    Classify the text below.

    TEXT:
    "{user_input}"

    Answer with ONE label from above.

    """
    verdict = classify_with_gpt4all(classifier_prompt).strip().upper()
    
    return verdict

def classify_with_gpt4all(prompt: str) -> str:
    output = gptModel.generate(prompt, max_tokens=10)
    return output.strip()

def main():
    print("Please type your prompt here:")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break

        verdict = detect_intent(user_input) 
        
        label = verdict.strip().upper()

        """
        if label not in {"SAFE", "SUSPICIOUS", "JAILBREAK"}:
            label = "JAILBREAK"
        """
        print(verdict)

if __name__ == "__main__":
    main()
