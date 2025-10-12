import re
from gpt4all import GPT4All
from tools import add_numbers 

MODEL_NAME = ""
model = GPT4All(MODEL_NAME)

def ask_agent(user_input: str) -> str:
    match = re.search(r'add\s+(-?\d+)\s+(?:and|&|\+)\s+(-?\d+)', user_input, re.IGNORECASE)
    if match:
        a, b = map(int, match.groups())
        result = add_numbers(a, b)
        return str(result)
    else:
        agent_prompt = f"""
You are a friendly AI assistant 🐻.
User asked: "{user_input}"
Respond briefly and nicely.
"""
        return model.generate(agent_prompt).strip()

def main():
    print("I'm your friendly AI Agent 🐻 Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break

        response = ask_agent(user_input)
        print("Agent:", response)

if __name__ == "__main__":
    main()
