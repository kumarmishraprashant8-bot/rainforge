"""
AI Copilot API Endpoints
Natural language assistant for RWH queries.
"""

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.services.ai_copilot_service import get_ai_copilot_service

router = APIRouter(prefix="/copilot", tags=["AI Copilot"])


class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class DocumentParseRequest(BaseModel):
    user_id: str
    document_name: str
    document_type: Optional[str] = None


@router.post("/chat")
async def chat(request: ChatRequest):
    """Process chat message and get AI response."""
    service = get_ai_copilot_service()
    return await service.chat(
        request.user_id, request.message,
        request.session_id, request.context
    )

@router.post("/parse-document")
async def parse_document(
    user_id: str,
    document_name: str,
    file: UploadFile = File(...),
    document_type: Optional[str] = None
):
    """Parse uploaded document and extract RWH-relevant data."""
    service = get_ai_copilot_service()
    content = await file.read()
    return await service.parse_document(user_id, content, document_name, document_type)

@router.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str, project_id: Optional[int] = None):
    """Get proactive recommendations for user."""
    service = get_ai_copilot_service()
    return await service.get_recommendations(user_id, project_id)
