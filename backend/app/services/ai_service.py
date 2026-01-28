"""AI Assistant service using OpenAI/LLM."""

from typing import Optional, List, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
import json

from app.core.config import settings
from app.models.chat import AIChatSession, AIChatMessage
from app.models.booking import Booking, BookingStatus
from app.models.room import Room, RoomStatus
from app.models.guest import Guest


class AIService:
    """Service class for AI assistant operations."""

    def __init__(self, db: Session):
        self.db = db
        self.model = settings.AI_MODEL
        self.temperature = settings.AI_TEMPERATURE

    def create_session(
        self,
        user_id: Optional[int] = None,
        guest_id: Optional[int] = None,
        session_type: str = "admin",
        hotel_id: Optional[int] = None,
    ) -> AIChatSession:
        """Create a new AI chat session."""
        session = AIChatSession(
            user_id=user_id,
            guest_id=guest_id,
            session_type=session_type,
            context={"hotel_id": hotel_id} if hotel_id else {},
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    async def process_message(
        self,
        session_id: int,
        message: str,
    ) -> Dict[str, Any]:
        """Process a user message and generate AI response."""
        session = self.db.query(AIChatSession).filter(
            AIChatSession.id == session_id
        ).first()

        if not session:
            raise ValueError("Session not found")

        # Save user message
        user_message = AIChatMessage(
            session_id=session_id,
            role="user",
            content=message,
        )
        self.db.add(user_message)
        self.db.commit()

        # Get hotel context
        hotel_id = session.context.get("hotel_id")

        # Analyze intent and get relevant data
        intent = self._analyze_intent(message)
        context_data = self._get_context_data(hotel_id, intent)

        # Generate response
        response = await self._generate_response(
            message=message,
            intent=intent,
            context_data=context_data,
            session=session,
        )

        # Save AI response
        ai_message = AIChatMessage(
            session_id=session_id,
            role="assistant",
            content=response["message"],
            tokens_used=response.get("tokens_used", 0),
        )
        self.db.add(ai_message)
        self.db.commit()

        return response

    def _analyze_intent(self, message: str) -> str:
        """Analyze user message to determine intent."""
        message_lower = message.lower()

        # Room availability
        if any(word in message_lower for word in ["available", "vacancy", "empty", "free room"]):
            return "check_availability"

        # Bookings
        if any(word in message_lower for word in ["booking", "reservation", "check-in", "check-out"]):
            return "booking_info"

        # Today's activity
        if any(word in message_lower for word in ["today", "arrivals", "departures"]):
            return "today_activity"

        # Revenue/financial
        if any(word in message_lower for word in ["revenue", "income", "money", "payment"]):
            return "financial_info"

        # Guest info
        if any(word in message_lower for word in ["guest", "vip", "customer"]):
            return "guest_info"

        # Occupancy
        if any(word in message_lower for word in ["occupancy", "occupied", "utilization"]):
            return "occupancy_info"

        return "general"

    def _get_context_data(
        self,
        hotel_id: Optional[int],
        intent: str,
    ) -> Dict[str, Any]:
        """Get relevant context data based on intent."""
        if not hotel_id:
            return {}

        today = date.today()
        context = {}

        if intent in ["check_availability", "occupancy_info"]:
            # Room availability
            total_rooms = self.db.query(Room).filter(
                Room.hotel_id == hotel_id,
                Room.is_active == True,
            ).count()

            available = self.db.query(Room).filter(
                Room.hotel_id == hotel_id,
                Room.status == RoomStatus.AVAILABLE,
            ).count()

            occupied = self.db.query(Room).filter(
                Room.hotel_id == hotel_id,
                Room.status == RoomStatus.CHECKED_IN,
            ).count()

            context["rooms"] = {
                "total": total_rooms,
                "available": available,
                "occupied": occupied,
                "occupancy_rate": round((occupied / total_rooms * 100), 1) if total_rooms > 0 else 0,
            }

        if intent in ["booking_info", "today_activity"]:
            # Today's bookings
            today_check_ins = self.db.query(Booking).filter(
                Booking.hotel_id == hotel_id,
                Booking.check_in_date == today,
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]),
            ).count()

            today_check_outs = self.db.query(Booking).filter(
                Booking.hotel_id == hotel_id,
                Booking.check_out_date == today,
                Booking.status == BookingStatus.CHECKED_IN,
            ).count()

            context["today"] = {
                "check_ins": today_check_ins,
                "check_outs": today_check_outs,
                "date": str(today),
            }

        if intent == "guest_info":
            # VIP guests
            vip_count = self.db.query(Guest).filter(
                Guest.hotel_id == hotel_id,
                Guest.is_vip == True,
            ).count()

            total_guests = self.db.query(Guest).filter(
                Guest.hotel_id == hotel_id,
            ).count()

            context["guests"] = {
                "total": total_guests,
                "vip_count": vip_count,
            }

        return context

    async def _generate_response(
        self,
        message: str,
        intent: str,
        context_data: Dict[str, Any],
        session: AIChatSession,
    ) -> Dict[str, Any]:
        """Generate AI response based on intent and context."""
        # For now, generate rule-based responses
        # In production, this would call OpenAI API

        response_text = self._generate_rule_based_response(intent, context_data, message)

        suggestions = self._get_suggestions(intent)

        return {
            "message": response_text,
            "session_id": session.id,
            "suggestions": suggestions,
            "actions": [],
            "tokens_used": 0,
        }

    def _generate_rule_based_response(
        self,
        intent: str,
        context: Dict[str, Any],
        message: str,
    ) -> str:
        """Generate rule-based response for common queries."""
        if intent == "check_availability" and "rooms" in context:
            rooms = context["rooms"]
            return (
                f"Currently, we have {rooms['available']} rooms available out of "
                f"{rooms['total']} total rooms. Our current occupancy rate is "
                f"{rooms['occupancy_rate']}%."
            )

        if intent == "today_activity" and "today" in context:
            today = context["today"]
            return (
                f"For today ({today['date']}):\n"
                f"- Expected check-ins: {today['check_ins']}\n"
                f"- Expected check-outs: {today['check_outs']}"
            )

        if intent == "occupancy_info" and "rooms" in context:
            rooms = context["rooms"]
            return (
                f"Current occupancy status:\n"
                f"- Occupied rooms: {rooms['occupied']}\n"
                f"- Available rooms: {rooms['available']}\n"
                f"- Occupancy rate: {rooms['occupancy_rate']}%"
            )

        if intent == "guest_info" and "guests" in context:
            guests = context["guests"]
            return (
                f"Guest statistics:\n"
                f"- Total guests in database: {guests['total']}\n"
                f"- VIP guests: {guests['vip_count']}"
            )

        # Default response
        return (
            "I'm your hotel AI assistant. I can help you with:\n"
            "- Room availability and occupancy\n"
            "- Today's check-ins and check-outs\n"
            "- Guest information\n"
            "- Revenue and booking statistics\n\n"
            "How can I assist you?"
        )

    def _get_suggestions(self, intent: str) -> List[str]:
        """Get follow-up suggestions based on intent."""
        suggestions_map = {
            "check_availability": [
                "Show today's check-ins",
                "What's the occupancy for this week?",
                "List available deluxe rooms",
            ],
            "today_activity": [
                "Show VIP arrivals",
                "Rooms needing attention",
                "Revenue summary",
            ],
            "occupancy_info": [
                "Forecast for next week",
                "Compare with last month",
                "Room type breakdown",
            ],
            "guest_info": [
                "VIP guests arriving today",
                "Repeat customers",
                "Guest preferences",
            ],
            "general": [
                "What rooms are available?",
                "Today's arrivals",
                "Occupancy rate",
                "Revenue summary",
            ],
        }

        return suggestions_map.get(intent, suggestions_map["general"])

    def get_ai_insights(self, hotel_id: int) -> List[Dict[str, Any]]:
        """Generate AI-powered insights for the dashboard."""
        insights = []
        today = date.today()

        # Check occupancy
        total_rooms = self.db.query(Room).filter(
            Room.hotel_id == hotel_id,
            Room.is_active == True,
        ).count()

        occupied = self.db.query(Room).filter(
            Room.hotel_id == hotel_id,
            Room.status.in_([RoomStatus.CHECKED_IN, RoomStatus.BOOKED]),
        ).count()

        occupancy_rate = (occupied / total_rooms * 100) if total_rooms > 0 else 0

        if occupancy_rate < 50:
            insights.append({
                "type": "warning",
                "title": "Low Occupancy Alert",
                "message": f"Current occupancy is {occupancy_rate:.1f}%. Consider running promotions.",
                "priority": 2,
                "action": "Create promotion",
            })

        # Check pending bookings
        pending = self.db.query(Booking).filter(
            Booking.hotel_id == hotel_id,
            Booking.status == BookingStatus.PENDING,
        ).count()

        if pending > 5:
            insights.append({
                "type": "alert",
                "title": "Pending Bookings",
                "message": f"You have {pending} bookings waiting for confirmation.",
                "priority": 1,
                "action": "Review bookings",
            })

        # VIP arrivals
        vip_arrivals = self.db.query(Booking).join(Guest).filter(
            Booking.hotel_id == hotel_id,
            Booking.check_in_date == today,
            Guest.is_vip == True,
        ).count()

        if vip_arrivals > 0:
            insights.append({
                "type": "suggestion",
                "title": "VIP Arrivals Today",
                "message": f"{vip_arrivals} VIP guest(s) arriving today.",
                "priority": 1,
            })

        return sorted(insights, key=lambda x: x["priority"])
