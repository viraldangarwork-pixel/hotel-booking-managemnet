"""API v1 module."""

from fastapi import APIRouter

from .endpoints import auth, users, hotels, rooms, bookings, guests, payments, chat, dashboard, settings

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(hotels.router, prefix="/hotels", tags=["Hotels"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["Rooms"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(guests.router, prefix="/guests", tags=["Guests"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
