"""Chat endpoints for WhatsApp and AI."""

from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.guest import Guest
from app.models.room import Room, RoomStatus
from app.models.booking import Booking, BookingStatus
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
        direction=MessageDirection.outbound,
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

    chat.status = ChatStatus.resolved
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


# ============ Data Summary for Chat Panel ============

@router.get("/ai/data-summary")
def get_data_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get hotel data summary for the chat panel."""
    today = date.today()

    # Room stats
    total_rooms = db.query(func.count(Room.id)).scalar() or 0
    available_rooms = db.query(func.count(Room.id)).filter(Room.status == RoomStatus.available).scalar() or 0
    occupied_rooms = db.query(func.count(Room.id)).filter(Room.status == RoomStatus.checked_in).scalar() or 0
    booked_rooms = db.query(func.count(Room.id)).filter(Room.status == RoomStatus.booked).scalar() or 0
    maintenance_rooms = db.query(func.count(Room.id)).filter(Room.status == RoomStatus.maintenance).scalar() or 0

    # Today's check-ins/check-outs
    todays_checkins = db.query(Booking).filter(
        Booking.check_in_date == today,
        Booking.status.in_([BookingStatus.confirmed, BookingStatus.pending]),
    ).all()

    todays_checkouts = db.query(Booking).filter(
        Booking.check_out_date == today,
        Booking.status == BookingStatus.checked_in,
    ).all()

    # Load guest info for today's bookings
    checkin_list = []
    for b in todays_checkins:
        guest = db.query(Guest).filter(Guest.id == b.guest_id).first()
        room = db.query(Room).filter(Room.id == b.room_id).first()
        checkin_list.append({
            "booking_ref": b.booking_ref,
            "guest_name": f"{guest.first_name} {guest.last_name}" if guest else "Unknown",
            "room_number": room.room_number if room else "N/A",
            "status": b.status.value if b.status else "pending",
        })

    checkout_list = []
    for b in todays_checkouts:
        guest = db.query(Guest).filter(Guest.id == b.guest_id).first()
        room = db.query(Room).filter(Room.id == b.room_id).first()
        checkout_list.append({
            "booking_ref": b.booking_ref,
            "guest_name": f"{guest.first_name} {guest.last_name}" if guest else "Unknown",
            "room_number": room.room_number if room else "N/A",
            "actual_check_in": b.actual_check_in.isoformat() if b.actual_check_in else None,
        })

    # Guest stats
    total_guests = db.query(func.count(Guest.id)).scalar() or 0
    vip_guests = db.query(func.count(Guest.id)).filter(Guest.is_vip == True).scalar() or 0

    # Active bookings
    active_bookings = db.query(func.count(Booking.id)).filter(
        Booking.status.in_([BookingStatus.confirmed, BookingStatus.pending, BookingStatus.checked_in])
    ).scalar() or 0

    return {
        "rooms": {
            "total": total_rooms,
            "available": available_rooms,
            "occupied": occupied_rooms,
            "booked": booked_rooms,
            "maintenance": maintenance_rooms,
        },
        "today": {
            "check_ins": checkin_list,
            "check_outs": checkout_list,
            "check_in_count": len(checkin_list),
            "check_out_count": len(checkout_list),
        },
        "guests": {
            "total": total_guests,
            "vip": vip_guests,
        },
        "bookings": {
            "active": active_bookings,
        },
    }


def _generate_smart_response(content: str, db: Session) -> str:
    """Generate a context-aware response by querying the database."""
    lower = content.lower().strip()
    today = date.today()

    # Room availability query
    if any(kw in lower for kw in ["room", "available", "availability", "vacant", "free room"]):
        available = db.query(Room).filter(Room.status == RoomStatus.available).all()
        if available:
            room_list = ", ".join([f"Room {r.room_number} (Floor {r.floor})" for r in available[:10]])
            return f"There are {len(available)} available rooms: {room_list}."
        return "No rooms are currently available."

    # Today's check-ins
    if any(kw in lower for kw in ["today check-in", "today's check-in", "checkin today", "check in today", "arriving today"]):
        checkins = db.query(Booking).filter(
            Booking.check_in_date == today,
            Booking.status.in_([BookingStatus.confirmed, BookingStatus.pending]),
        ).all()
        if checkins:
            lines = []
            for b in checkins:
                guest = db.query(Guest).filter(Guest.id == b.guest_id).first()
                room = db.query(Room).filter(Room.id == b.room_id).first()
                name = f"{guest.first_name} {guest.last_name}" if guest else "Unknown"
                rnum = room.room_number if room else "N/A"
                lines.append(f"- {name} -> Room {rnum} (Ref: {b.booking_ref})")
            return f"Today's expected check-ins ({len(checkins)}):\n" + "\n".join(lines)
        return "No check-ins expected today."

    # Today's check-outs
    if any(kw in lower for kw in ["today check-out", "today's check-out", "checkout today", "check out today", "departing today"]):
        checkouts = db.query(Booking).filter(
            Booking.check_out_date == today,
            Booking.status == BookingStatus.checked_in,
        ).all()
        if checkouts:
            lines = []
            for b in checkouts:
                guest = db.query(Guest).filter(Guest.id == b.guest_id).first()
                room = db.query(Room).filter(Room.id == b.room_id).first()
                name = f"{guest.first_name} {guest.last_name}" if guest else "Unknown"
                rnum = room.room_number if room else "N/A"
                lines.append(f"- {name} from Room {rnum} (Ref: {b.booking_ref})")
            return f"Today's expected check-outs ({len(checkouts)}):\n" + "\n".join(lines)
        return "No check-outs expected today."

    # Guest search
    if any(kw in lower for kw in ["find guest", "search guest", "guest info", "guest details", "lookup guest"]):
        # Try to extract a name
        for prefix in ["find guest ", "search guest ", "guest info ", "guest details ", "lookup guest "]:
            if lower.startswith(prefix):
                search_term = content[len(prefix):].strip()
                guests = db.query(Guest).filter(
                    (Guest.first_name.ilike(f"%{search_term}%")) |
                    (Guest.last_name.ilike(f"%{search_term}%")) |
                    (Guest.phone.ilike(f"%{search_term}%"))
                ).limit(5).all()
                if guests:
                    lines = []
                    for g in guests:
                        vip = " [VIP]" if g.is_vip else ""
                        lines.append(f"- {g.first_name} {g.last_name} | {g.phone} | {g.email or 'No email'}{vip}")
                    return f"Found {len(guests)} guest(s):\n" + "\n".join(lines)
                return f"No guests found matching '{search_term}'."
        return "Please specify a guest name or phone, e.g., 'Find guest John'"

    # Booking search
    if any(kw in lower for kw in ["find booking", "search booking", "booking info", "booking ref"]):
        for prefix in ["find booking ", "search booking ", "booking info ", "booking ref "]:
            if lower.startswith(prefix):
                ref_term = content[len(prefix):].strip()
                booking = db.query(Booking).filter(Booking.booking_ref.ilike(f"%{ref_term}%")).first()
                if booking:
                    guest = db.query(Guest).filter(Guest.id == booking.guest_id).first()
                    room = db.query(Room).filter(Room.id == booking.room_id).first()
                    name = f"{guest.first_name} {guest.last_name}" if guest else "Unknown"
                    rnum = room.room_number if room else "N/A"
                    return (
                        f"Booking {booking.booking_ref}:\n"
                        f"- Guest: {name}\n"
                        f"- Room: {rnum}\n"
                        f"- Check-in: {booking.check_in_date}\n"
                        f"- Check-out: {booking.check_out_date}\n"
                        f"- Status: {booking.status.value}\n"
                        f"- Total: ${booking.total_amount}"
                    )
                return f"No booking found matching '{ref_term}'."
        return "Please specify a booking reference, e.g., 'Find booking BK240101ABCD'"

    # Occupancy
    if any(kw in lower for kw in ["occupancy", "how many occupied", "occupied rooms"]):
        total = db.query(func.count(Room.id)).scalar() or 0
        occupied = db.query(func.count(Room.id)).filter(
            Room.status.in_([RoomStatus.checked_in, RoomStatus.booked])
        ).scalar() or 0
        rate = round((occupied / total * 100), 1) if total > 0 else 0
        return f"Current occupancy: {occupied}/{total} rooms ({rate}%). {total - occupied} rooms available."

    # Guest count
    if any(kw in lower for kw in ["how many guest", "total guest", "guest count"]):
        total = db.query(func.count(Guest.id)).scalar() or 0
        vip = db.query(func.count(Guest.id)).filter(Guest.is_vip == True).scalar() or 0
        return f"Total guests in system: {total} ({vip} VIP guests)."

    # Revenue
    if any(kw in lower for kw in ["revenue", "income", "earnings"]):
        total_rev = db.query(func.sum(Booking.total_amount)).filter(
            Booking.status.in_([BookingStatus.checked_in, BookingStatus.checked_out])
        ).scalar() or 0
        return f"Total revenue from completed/active bookings: ${total_rev:,.2f}"

    # Default response with suggestions
    return (
        "I can help you with hotel data. Try asking:\n"
        "- 'Show available rooms'\n"
        "- 'Today's check-ins'\n"
        "- 'Today's check-outs'\n"
        "- 'Find guest [name]'\n"
        "- 'Find booking [ref]'\n"
        "- 'Current occupancy'\n"
        "- 'Total guests'\n"
        "- 'Revenue summary'"
    )


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

    # Generate smart response by querying the database
    ai_response = _generate_smart_response(message_data.content, db)

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
