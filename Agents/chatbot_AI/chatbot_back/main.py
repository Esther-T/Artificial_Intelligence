from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import ChatRequest, ImageRequest
from ai import generate_text, generate_image

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok"}
    
@app.post("/chat")
def chat(req: ChatRequest):
    reply = generate_text(req.message)
    return {"reply": reply}


@app.post("/image")
def image(req: ImageRequest):
    image_url = generate_image(req.prompt)
    return {"image_url": image_url}

