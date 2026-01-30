"""WhatsApp Business API integration service."""

from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.chat import (
    WhatsAppChat,
    WhatsAppMessage,
    MessageDirection,
    MessageStatus,
    ChatStatus,
)
from app.models.guest import Guest


class WhatsAppService:
    """Service class for WhatsApp Business API integration."""

    def __init__(self, db: Session):
        self.db = db
        self.api_url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json",
        }

    async def send_message(
        self,
        to: str,
        message: str,
        chat_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Send a text message via WhatsApp."""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/messages",
                headers=self.headers,
                json=payload,
            )

        result = response.json()

        # Record the message if chat_id provided
        if chat_id and response.status_code == 200:
            self._record_outbound_message(
                chat_id=chat_id,
                content=message,
                message_id=result.get("messages", [{}])[0].get("id"),
            )

        return result

    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "en",
        components: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Send a template message via WhatsApp."""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
            },
        }

        if components:
            payload["template"]["components"] = components

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/messages",
                headers=self.headers,
                json=payload,
            )

        return response.json()

    async def send_booking_confirmation(
        self,
        to: str,
        guest_name: str,
        booking_ref: str,
        check_in_date: str,
        check_out_date: str,
        room_type: str,
    ) -> Dict[str, Any]:
        """Send booking confirmation message."""
        message = f"""
Hello {guest_name}!

Your booking has been confirmed.

Booking Reference: {booking_ref}
Check-in: {check_in_date}
Check-out: {check_out_date}
Room Type: {room_type}

We look forward to welcoming you!

Reply with 'HELP' for assistance.
"""
        return await self.send_message(to, message.strip())

    async def send_check_in_reminder(
        self,
        to: str,
        guest_name: str,
        booking_ref: str,
        check_in_date: str,
        check_in_time: str,
    ) -> Dict[str, Any]:
        """Send check-in reminder message."""
        message = f"""
Hello {guest_name}!

Reminder: Your check-in is tomorrow!

Booking Reference: {booking_ref}
Check-in Date: {check_in_date}
Check-in Time: {check_in_time}

See you soon!
"""
        return await self.send_message(to, message.strip())

    def process_incoming_message(
        self,
        wa_id: str,
        message_id: str,
        message_type: str,
        content: Optional[str] = None,
        media_url: Optional[str] = None,
        profile_name: Optional[str] = None,
    ) -> WhatsAppMessage:
        """Process and store incoming WhatsApp message."""
        # Find or create chat
        chat = self.db.query(WhatsAppChat).filter(
            WhatsAppChat.wa_id == wa_id
        ).first()

        if not chat:
            # Try to find associated guest
            guest = self.db.query(Guest).filter(
                Guest.whatsapp_number == wa_id
            ).first()

            chat = WhatsAppChat(
                guest_id=guest.id if guest else None,
                wa_id=wa_id,
                phone_number=wa_id,
                profile_name=profile_name,
                status=ChatStatus.active,
            )
            self.db.add(chat)
            self.db.flush()

        # Create message record
        message = WhatsAppMessage(
            chat_id=chat.id,
            message_id=message_id,
            direction=MessageDirection.inbound,
            message_type=message_type,
            content=content,
            media_url=media_url,
            sent_at=datetime.now(),
        )

        self.db.add(message)

        # Update chat
        chat.last_message_at = datetime.now()
        chat.unread_count += 1

        self.db.commit()
        self.db.refresh(message)

        return message

    def _record_outbound_message(
        self,
        chat_id: int,
        content: str,
        message_id: Optional[str] = None,
        is_bot: bool = False,
        sent_by: Optional[int] = None,
    ) -> WhatsAppMessage:
        """Record an outbound message."""
        message = WhatsAppMessage(
            chat_id=chat_id,
            message_id=message_id,
            direction=MessageDirection.outbound,
            message_type="text",
            content=content,
            status=MessageStatus.sent,
            is_bot_message=is_bot,
            sent_by=sent_by,
            sent_at=datetime.now(),
        )

        self.db.add(message)

        # Update chat
        chat = self.db.query(WhatsAppChat).filter(WhatsAppChat.id == chat_id).first()
        chat.last_message_at = datetime.now()

        self.db.commit()
        self.db.refresh(message)

        return message

    def update_message_status(
        self,
        message_id: str,
        status: str,
        timestamp: Optional[datetime] = None,
    ):
        """Update message delivery status from webhook."""
        message = self.db.query(WhatsAppMessage).filter(
            WhatsAppMessage.message_id == message_id
        ).first()

        if message:
            if status == "delivered":
                message.status = MessageStatus.delivered
                message.delivered_at = timestamp or datetime.now()
            elif status == "read":
                message.status = MessageStatus.read
                message.read_at = timestamp or datetime.now()
            elif status == "failed":
                message.status = MessageStatus.failed

            self.db.commit()

    def assign_chat_to_agent(
        self,
        chat_id: int,
        agent_id: int,
    ) -> WhatsAppChat:
        """Assign chat to a human agent."""
        chat = self.db.query(WhatsAppChat).filter(WhatsAppChat.id == chat_id).first()
        if not chat:
            raise ValueError("Chat not found")

        chat.is_bot_active = False
        chat.assigned_to = agent_id
        chat.human_takeover_requested = False

        self.db.commit()
        self.db.refresh(chat)

        return chat

    def enable_bot(self, chat_id: int) -> WhatsAppChat:
        """Re-enable bot for a chat."""
        chat = self.db.query(WhatsAppChat).filter(WhatsAppChat.id == chat_id).first()
        if not chat:
            raise ValueError("Chat not found")

        chat.is_bot_active = True
        chat.assigned_to = None

        self.db.commit()
        self.db.refresh(chat)

        return chat

    def resolve_chat(self, chat_id: int) -> WhatsAppChat:
        """Mark chat as resolved."""
        chat = self.db.query(WhatsAppChat).filter(WhatsAppChat.id == chat_id).first()
        if not chat:
            raise ValueError("Chat not found")

        chat.status = ChatStatus.resolved
        self.db.commit()
        self.db.refresh(chat)

        return chat

    def get_unread_chats(self) -> List[WhatsAppChat]:
        """Get all chats with unread messages."""
        return self.db.query(WhatsAppChat).filter(
            WhatsAppChat.unread_count > 0,
            WhatsAppChat.status == ChatStatus.active,
        ).order_by(WhatsAppChat.last_message_at.desc()).all()

    def get_chats_needing_attention(self) -> List[WhatsAppChat]:
        """Get chats that need human attention."""
        return self.db.query(WhatsAppChat).filter(
            WhatsAppChat.human_takeover_requested == True,
            WhatsAppChat.status == ChatStatus.active,
        ).all()
