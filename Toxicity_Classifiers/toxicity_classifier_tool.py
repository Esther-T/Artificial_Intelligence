import torch
import torch.nn.functional as F
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import requests

MAX_LENGTH = 500 

def pull_Reddit_Posts():
    posts = []
    headers = {"User-Agent": "my-student-project/0.1 by myRedditUsername"}

    url = f"https://www.reddit.com/r/compsci/new.json?t=month&limit=100"
    params = {
        "t": "month",
        "limit": 5,
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error fetching posts: {response.status_code}")
    
    else:
        data = response.json()
        children = data["data"]["children"]

        for child in children:
            post_data = child["data"]
            text = post_data.get("selftext", "")
            if len(text) <= MAX_LENGTH:
                posts.append(text)
    return posts
    

def get_toxicity_score(user_str):
    tokenizer = RobertaTokenizer.from_pretrained('s-nlp/roberta_toxicity_classifier')
    model = RobertaForSequenceClassification.from_pretrained('s-nlp/roberta_toxicity_classifier')
    batch = tokenizer.encode(user_str, return_tensors="pt")
    output = model(batch)
    probs = F.softmax(output.logits, dim=1)
    
    return probs[0][1].item()

def main():
    scores = []
    posts = []
    
    posts = pull_Reddit_Posts()
    
    for post in posts:
        score = get_toxicity_score(post)
        scores.append(score)
        
    average_toxicity = sum(scores) / len(scores)
    print("Average toxicity:", average_toxicity)
    
if __name__ == "__main__":
    main()