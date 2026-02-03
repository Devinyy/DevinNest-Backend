from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gpt-3.5-turbo"
    temperature: float = Field(0.7, ge=0.0, le=2.0)

class ChatResponse(BaseModel):
    id: str
    choices: List[dict]
    created: int
    model: str
