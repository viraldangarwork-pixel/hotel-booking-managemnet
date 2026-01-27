"""Chat schemas for WhatsApp and AI conversations."""

from typing import Optional, List, Dict, Any
from datetime import datetime

from .base import BaseSchema, IDSchema
from app.models.chat import MessageDirection, MessageStatus, ChatStatus


class WhatsAppMessageCreate(BaseSchema):
    """Schema for creating/sending a WhatsApp message."""

    chat_id: int
    content: str
    message_type: str = "text"
    media_url: Optional[str] = None


class WhatsAppMessageResponse(IDSchema):
    """Schema for WhatsApp message response."""

    chat_id: int
    message_id: Optional[str] = None
    direction: MessageDirection
    message_type: str
    content: Optional[str] = None
    media_url: Optional[str] = None
    status: Optional[MessageStatus] = None
    is_bot_message: bool
    sent_by: Optional[int] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None


class WhatsAppChatResponse(IDSchema):
    """Schema for WhatsApp chat response."""

    guest_id: Optional[int] = None
    wa_id: str
    phone_number: str
    profile_name: Optional[str] = None
    status: ChatStatus
    is_bot_active: bool
    human_takeover_requested: bool
    assigned_to: Optional[int] = None
    language: str
    last_message_at: Optional[datetime] = None
    unread_count: int
    messages: List[WhatsAppMessageResponse] = []


class WhatsAppWebhookPayload(BaseSchema):
    """Schema for WhatsApp webhook payload."""

    object: str
    entry: List[Dict[str, Any]]


class AIChatMessageCreate(BaseSchema):
    """Schema for creating an AI chat message."""

    content: str


class AIChatMessageResponse(IDSchema):
    """Schema for AI chat message response."""

    session_id: int
    role: str
    content: str
    tokens_used: int
    function_call: Optional[Dict[str, Any]] = None
    function_response: Optional[Dict[str, Any]] = None


class AIChatSessionResponse(IDSchema):
    """Schema for AI chat session response."""

    user_id: Optional[int] = None
    guest_id: Optional[int] = None
    session_type: str
    context: Dict[str, Any]
    summary: Optional[str] = None
    is_active: bool
    messages: List[AIChatMessageResponse] = []


class AIChatResponse(BaseSchema):
    """Schema for AI chat response."""

    message: str
    session_id: int
    suggestions: List[str] = []
    actions: List[Dict[str, Any]] = []
