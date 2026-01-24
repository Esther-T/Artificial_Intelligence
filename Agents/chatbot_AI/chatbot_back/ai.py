import os
import requests
import json


API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise RuntimeError("API_KEY not set")
    
def generate_text(prompt: str):    
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
    "Authorization": "Bearer " + API_KEY,
    "Content-Type": "application/json",
    },
    data=json.dumps({
    "model": "google/gemma-3-27b-it:free",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": prompt
          },
        ]
      }
    ]
    })
    )
    content = response.json()

    return content["choices"][0]["message"]["content"]


def generate_image(prompt: str):
   # under construction
   return ""
