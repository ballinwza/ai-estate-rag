from fastapi import APIRouter

from app.api.v1.endpoints import chat, documents, health

api_router = APIRouter()

# Register Endpoints
api_router.include_router(
    health.health_router, prefix="/connection", tags=["Health & Demo"]
)
# api_router.include_router(
#     audit.history_router,
#     prefix="/audit",
#     tags=["History & Logging"],
# )
api_router.include_router(chat.chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(
    documents.document_router,
)
