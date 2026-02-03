from fastapi import APIRouter, HTTPException, Depends
from app.llm.schemas import ChatRequest, ChatResponse
from app.llm.service import llm_service
from app.backstage.schemas import ApiResponse

router = APIRouter()

@router.post("/chat", response_model=ApiResponse[ChatResponse])
async def chat_completion(request: ChatRequest):
    """
    Generate a chat completion using the configured LLM.
    """
    try:
        response = await llm_service.generate_response(request)
        return ApiResponse(data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
