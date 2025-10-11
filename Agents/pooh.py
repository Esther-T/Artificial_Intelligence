import json
from gpt4all import GPT4All
from mcp import handle_request

# available_models = GPT4All.list_models()
# print("Available GPT4All models:", available_models)

model = GPT4All("C:\\Users\\tanes\\Documents\\Projects\\AI\\Agents\\Llama-3.2-1B-Instruct-Q3_K_XL.gguf")

def ask_agent(prompt: str) -> str:
    return model.generate(prompt)

def main():
    print("I'm your friendly neighborhood Pooh Bear 😊 🐻 Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        agent_prompt = f"""
        You are a small, yellow, naive bear. You are friendly, playful, and polite.
        User asked: "{user_input}"
        
        If the user asks to "add x and y" where x and y are integers:
            - Extract the numbers x and y
            - Output ONLY JSON like this:
              {{
                  "tool": "add_numbers",
                  "parameters": {{"a": x, "b": y}},
                  "request_id": "1"
              }}
            - Do NOT add any extra text.

        - Output ONLY a single-line reply as the bear
        - Do NOT invent new questions
        - Do Not invent new context
        - Do NOT invent new paragraphs
        - Do NOT explain yourself
        - Do NOT describe your behavior
        - Do NOT give instructions
        - Do NOT call any tools
        - Keep it under 100 characters
        - Output NOTHING except the bear’s reply
        - No greetings, no repeated messages, no extra commentary
        
        """



        response = ask_agent(agent_prompt).strip()
        try:
            mcp_response = handle_request(response)
            print("Pooh:", mcp_response)
        except Exception as e:
            # prompt below doesn't work
            print(response)

if __name__ == "__main__":
    main()
