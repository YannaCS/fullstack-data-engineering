from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.models import User, Conversation, Message
from app.api.auth import get_current_user

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[int] = None


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: str


class ConversationResponse(BaseModel):
    id: int
    title: Optional[str]
    created_at: str
    updated_at: str
    messages: List[MessageResponse]


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int


@router.post("/query")
async def chat_query(
    request_data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """
    Query the chat system (non-streaming version)
    For streaming, use the WebSocket endpoint
    """
    from app.services.chat_service import ChatService
    
    # Get or create conversation
    if request_data.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == request_data.conversation_id,
                Conversation.user_id == current_user.id
            )
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=current_user.id,
            title=request_data.query[:50] + "..." if len(request_data.query) > 50 else request_data.query
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request_data.query
    )
    db.add(user_message)
    await db.commit()
    
    # Get chat service
    vector_store = request.app.state.vector_store
    chat_service = ChatService(vector_store)
    
    # Collect streamed response
    response_parts = []
    sources = []
    
    async for chunk in chat_service.stream_chat_response(
        query=request_data.query,
        conversation_id=str(conversation.id),
        user_id=str(current_user.id)
    ):
        if chunk["type"] == "content":
            response_parts.append(chunk["content"])
        elif chunk["type"] == "complete":
            sources = chunk.get("sources", [])
    
    full_response = "".join(response_parts)
    
    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=full_response,
        metadata={"sources": sources}
    )
    db.add(assistant_message)
    
    # Update conversation
    conversation.updated_at = datetime.utcnow()
    await db.commit()
    
    return {
        "conversation_id": conversation.id,
        "response": full_response,
        "sources": sources
    }


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50
):
    """List all conversations for the current user"""
    
    # Get total count
    result = await db.execute(
        select(Conversation).where(Conversation.user_id == current_user.id)
    )
    all_convs = result.scalars().all()
    total = len(all_convs)
    
    # Get paginated results
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.updated_at))
        .offset(skip)
        .limit(limit)
    )
    conversations = result.scalars().all()
    
    # Load messages for each conversation
    conv_responses = []
    for conv in conversations:
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()
        
        conv_responses.append(
            ConversationResponse(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat(),
                messages=[
                    MessageResponse(
                        id=msg.id,
                        role=msg.role,
                        content=msg.content,
                        created_at=msg.created_at.isoformat()
                    )
                    for msg in messages
                ]
            )
        )
    
    return ConversationListResponse(
        conversations=conv_responses,
        total=total
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific conversation with all messages"""
    
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Load messages
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
        messages=[
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at.isoformat()
            )
            for msg in messages
        ]
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a conversation"""
    
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    await db.delete(conversation)
    await db.commit()
    
    return {"message": "Conversation deleted successfully"}