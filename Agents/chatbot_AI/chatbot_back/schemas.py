from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class ImageRequest(BaseModel):
    prompt: str
