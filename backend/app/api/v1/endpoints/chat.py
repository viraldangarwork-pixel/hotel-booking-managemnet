"""Chat endpoints for WhatsApp and AI."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.guest import Guest
from app.models.chat import (
    WhatsAppChat,
    WhatsAppMessage,
    AIChatSession,
    AIChatMessage,
    MessageDirection,
    ChatStatus,
)
from app.schemas.chat import (
    WhatsAppMessageCreate,
    WhatsAppChatResponse,
    AIChatMessageCreate,
    AIChatResponse,
    AIChatSessionResponse,
)

router = APIRouter()


# ============ WhatsApp Chat ============

@router.get("/whatsapp", response_model=List[WhatsAppChatResponse])
def list_whatsapp_chats(
    status: Optional[ChatStatus] = None,
    assigned_to: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List WhatsApp chats."""
    query = db.query(WhatsAppChat)

    if status:
        query = query.filter(WhatsAppChat.status == status)
    if assigned_to:
        query = query.filter(WhatsAppChat.assigned_to == assigned_to)

    chats = query.order_by(WhatsAppChat.last_message_at.desc()).offset(skip).limit(limit).all()

    # Load messages for each chat
    for chat in chats:
        chat.messages = db.query(WhatsAppMessage).filter(
            WhatsAppMessage.chat_id == chat.id
        ).order_by(WhatsAppMessage.created_at.desc()).limit(20).all()
        chat.messages.reverse()

    return chats


@router.get("/whatsapp/{chat_id}", response_model=WhatsAppChatResponse)
def get_whatsapp_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get WhatsApp chat with messages."""
    chat = db.query(WhatsAppChat).filter(WhatsAppChat.id == chat_id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    chat.messages = db.query(WhatsAppMessage).filter(
        WhatsAppMessage.chat_id == chat_id
    ).order_by(WhatsAppMessage.created_at).all()

    # Mark as read
    chat.unread_count = 0
    db.commit()

    return chat


@router.post("/whatsapp/{chat_id}/send", response_model=dict)
def send_whatsapp_message(
    chat_id: int,
    message_data: WhatsAppMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a WhatsApp message (manual/human)."""
    chat = db.query(WhatsAppChat).filter(WhatsAppChat.id == chat_id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    # Create message record
    message = WhatsAppMessage(
        chat_id=chat_id,
        direction=MessageDirection.OUTBOUND,
        message_type=message_data.message_type,
        content=message_data.content,
        media_url=message_data.media_url,
        is_bot_message=False,
        sent_by=current_user.id,
        sent_at=datetime.now(),
    )
    db.add(message)

    # Update chat
    chat.last_message_at = datetime.now()
    chat.is_bot_active = False  # Human took over

    db.commit()
    db.refresh(message)

    # TODO: Integrate with WhatsApp Business API to actually send the message
    # This would involve calling the WhatsApp API with the message content

    return {"status": "sent", "message_id": message.id}


@router.post("/whatsapp/{chat_id}/takeover")
def takeover_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Take over a WhatsApp chat from bot."""
    chat = db.query(WhatsAppChat).filter(WhatsAppChat.id == chat_id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    chat.is_bot_active = False
    chat.assigned_to = current_user.id
    chat.human_takeover_requested = False
    db.commit()

    return {"status": "success", "message": "Chat assigned to you"}


@router.post("/whatsapp/{chat_id}/enable-bot")
def enable_bot(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Re-enable bot for a chat."""
    chat = db.query(WhatsAppChat).filter(WhatsAppChat.id == chat_id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    chat.is_bot_active = True
    chat.assigned_to = None
    db.commit()

    return {"status": "success", "message": "Bot re-enabled"}


@router.post("/whatsapp/{chat_id}/resolve")
def resolve_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark chat as resolved."""
    chat = db.query(WhatsAppChat).filter(WhatsAppChat.id == chat_id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    chat.status = ChatStatus.RESOLVED
    db.commit()

    return {"status": "success", "message": "Chat marked as resolved"}


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook endpoint for WhatsApp Business API."""
    # Verify webhook
    if request.method == "GET":
        params = request.query_params
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge")

        if mode == "subscribe" and token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
            return int(challenge)
        raise HTTPException(status_code=403, detail="Verification failed")

    # Process incoming message
    body = await request.json()

    # TODO: Process WhatsApp webhook payload
    # 1. Parse incoming message
    # 2. Find or create chat
    # 3. Save message
    # 4. If bot active, generate AI response
    # 5. Send response via WhatsApp API

    return {"status": "received"}


# ============ AI Chat ============

@router.get("/ai/sessions", response_model=List[AIChatSessionResponse])
def list_ai_sessions(
    session_type: str = "admin",
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List AI chat sessions for current user."""
    query = db.query(AIChatSession).filter(
        AIChatSession.user_id == current_user.id,
        AIChatSession.session_type == session_type,
    )

    sessions = query.order_by(AIChatSession.updated_at.desc()).offset(skip).limit(limit).all()

    for session in sessions:
        session.messages = db.query(AIChatMessage).filter(
            AIChatMessage.session_id == session.id
        ).order_by(AIChatMessage.created_at.desc()).limit(5).all()
        session.messages.reverse()

    return sessions


@router.post("/ai/sessions", response_model=AIChatSessionResponse)
def create_ai_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new AI chat session."""
    session = AIChatSession(
        user_id=current_user.id,
        session_type="admin",
        context={"hotel_id": current_user.hotel_id},
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    session.messages = []
    return session


@router.get("/ai/sessions/{session_id}", response_model=AIChatSessionResponse)
def get_ai_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get AI chat session with messages."""
    session = db.query(AIChatSession).filter(
        AIChatSession.id == session_id,
        AIChatSession.user_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    session.messages = db.query(AIChatMessage).filter(
        AIChatMessage.session_id == session_id
    ).order_by(AIChatMessage.created_at).all()

    return session


@router.post("/ai/sessions/{session_id}/message", response_model=AIChatResponse)
def send_ai_message(
    session_id: int,
    message_data: AIChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to AI and get response."""
    session = db.query(AIChatSession).filter(
        AIChatSession.id == session_id,
        AIChatSession.user_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Save user message
    user_message = AIChatMessage(
        session_id=session_id,
        role="user",
        content=message_data.content,
    )
    db.add(user_message)
    db.commit()

    # TODO: Integrate with OpenAI/LLM to generate response
    # For now, return a placeholder
    ai_response = "I'm your hotel AI assistant. I can help you with room availability, bookings, and guest information. What would you like to know?"

    # Save AI message
    ai_message = AIChatMessage(
        session_id=session_id,
        role="assistant",
        content=ai_response,
        tokens_used=0,  # TODO: Track actual token usage
    )
    db.add(ai_message)
    db.commit()

    return AIChatResponse(
        message=ai_response,
        session_id=session_id,
        suggestions=[
            "Show today's check-ins",
            "What rooms are available?",
            "Revenue summary for this week",
        ],
        actions=[],
    )


@router.delete("/ai/sessions/{session_id}")
def delete_ai_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an AI chat session."""
    session = db.query(AIChatSession).filter(
        AIChatSession.id == session_id,
        AIChatSession.user_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    db.delete(session)
    db.commit()

    return {"status": "deleted"}
