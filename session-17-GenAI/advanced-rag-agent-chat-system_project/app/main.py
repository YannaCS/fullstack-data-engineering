from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.core.config import settings
from app.core.database import init_db
from app.api import documents, chat, auth
from app.services.vector_store import VectorStoreManager

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add("logs/app.log", rotation="500 MB", retention="10 days", level="DEBUG")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events"""
    logger.info("Starting Advanced RAG Agent Chat System...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize vector store
    vector_store_manager = VectorStoreManager()
    app.state.vector_store = vector_store_manager
    logger.info("Vector store initialized")
    
    yield
    
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


@app.get("/")
async def root():
    return {
        "message": "Advanced RAG Agent Chat System API",
        "version": settings.APP_VERSION,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.websocket("/ws/chat/{conversation_id}")
async def websocket_chat_endpoint(websocket: WebSocket, conversation_id: str):
    """WebSocket endpoint for real-time chat streaming"""
    from app.services.chat_service import ChatService
    
    await websocket.accept()
    chat_service = ChatService(app.state.vector_store)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            query = data.get("query", "")
            user_id = data.get("user_id", "anonymous")
            
            logger.info(f"Received query from user {user_id}: {query[:50]}...")
            
            # Stream response back to client
            async for chunk in chat_service.stream_chat_response(
                query=query,
                conversation_id=conversation_id,
                user_id=user_id
            ):
                await websocket.send_json(chunk)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for conversation {conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({"error": str(e)})
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )