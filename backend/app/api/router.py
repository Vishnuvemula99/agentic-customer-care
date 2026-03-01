from fastapi import APIRouter

from app.api.endpoints import chat, conversations, health

api_router = APIRouter()

# Health check
api_router.include_router(health.router, prefix="/api", tags=["Health"])

# Chat endpoints
api_router.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

# Conversation management
api_router.include_router(conversations.router, prefix="/api/conversations", tags=["Conversations"])
