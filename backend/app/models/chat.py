"""Chat models for WhatsApp and AI conversations."""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum, Boolean, JSON, DateTime
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class MessageDirection(str, enum.Enum):
    """Message direction enum."""

    inbound = "inbound"
    outbound = "outbound"


class MessageStatus(str, enum.Enum):
    """WhatsApp message status enum."""

    sent = "sent"
    delivered = "delivered"
    read = "read"
    failed = "failed"


class ChatStatus(str, enum.Enum):
    """Chat conversation status."""

    active = "active"
    resolved = "resolved"
    pending_human = "pending_human"
    closed = "closed"


class WhatsAppChat(BaseModel):
    """WhatsApp conversation model."""

    __tablename__ = "whatsapp_chats"

    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=True)

    # WhatsApp contact info
    wa_id = Column(String(20), nullable=False, index=True)  # WhatsApp ID
    phone_number = Column(String(20), nullable=False)
    profile_name = Column(String(255), nullable=True)

    # Conversation status
    status = Column(
        Enum(ChatStatus), default=ChatStatus.active, nullable=False
    )

    # Bot handling
    is_bot_active = Column(Boolean, default=True, nullable=False)
    human_takeover_requested = Column(Boolean, default=False, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Context for AI
    context = Column(JSON, default=dict)  # Conversation context for AI
    language = Column(String(10), default="en")

    # Last interaction
    last_message_at = Column(DateTime, nullable=True)
    unread_count = Column(Integer, default=0)

    # Relationships
    guest = relationship("Guest", back_populates="whatsapp_chats")
    messages = relationship("WhatsAppMessage", back_populates="chat", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WhatsAppChat {self.wa_id}>"


class WhatsAppMessage(BaseModel):
    """Individual WhatsApp message."""

    __tablename__ = "whatsapp_messages"

    chat_id = Column(Integer, ForeignKey("whatsapp_chats.id"), nullable=False)

    # Message identifiers
    message_id = Column(String(100), nullable=True, index=True)  # WhatsApp message ID

    # Message content
    direction = Column(
        Enum(MessageDirection), nullable=False
    )
    message_type = Column(String(20), default="text")  # text, image, document, etc.
    content = Column(Text, nullable=True)
    media_url = Column(String(500), nullable=True)

    # Status tracking (for outbound)
    status = Column(
        Enum(MessageStatus), default=MessageStatus.sent, nullable=True
    )

    # Bot or human sent
    is_bot_message = Column(Boolean, default=False, nullable=False)
    sent_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Timestamps
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    chat = relationship("WhatsAppChat", back_populates="messages")

    def __repr__(self):
        return f"<WhatsAppMessage {self.id}>"


class AIChatSession(BaseModel):
    """AI chat session for admin/guest interactions."""

    __tablename__ = "ai_chat_sessions"

    # Session can be for guest or staff
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=True)

    # Session type
    session_type = Column(String(20), default="admin")  # admin, guest, whatsapp

    # Context
    context = Column(JSON, default=dict)
    summary = Column(Text, nullable=True)

    # Active status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    messages = relationship("AIChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AIChatSession {self.id}>"


class AIChatMessage(BaseModel):
    """Individual AI chat message."""

    __tablename__ = "ai_chat_messages"

    session_id = Column(Integer, ForeignKey("ai_chat_sessions.id"), nullable=False)

    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # Token usage for cost tracking
    tokens_used = Column(Integer, default=0)

    # For function calls
    function_call = Column(JSON, nullable=True)
    function_response = Column(JSON, nullable=True)

    # Relationships
    session = relationship("AIChatSession", back_populates="messages")

    def __repr__(self):
        return f"<AIChatMessage {self.id}>"
