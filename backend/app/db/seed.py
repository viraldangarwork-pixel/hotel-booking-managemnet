"""
Database seeding script for initial setup.

Default Admin Credentials:
==========================
Email:    admin@hotel.com
Password: Admin@123

Run this script to create initial admin user and sample data.
"""

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.hotel import Hotel
from app.models.room import Room, RoomType, RoomStatus
from app.models.settings import HotelSettings, ThemeSettings


# ============================================
# DEFAULT ADMIN CREDENTIALS
# ============================================
ADMIN_EMAIL = "admin@hotel.com"
ADMIN_PASSWORD = "Admin@123"
ADMIN_NAME = "System Administrator"
# ============================================


def create_tables():
    """Create all database tables."""
    # Import all models so they are registered with Base
    from app.models import (
        User, Hotel, Room, RoomType, Booking, Guest,
        Payment, WhatsAppChat, WhatsAppMessage,
        AIChatSession, AIChatMessage, ThemeSettings, HotelSettings,
    )
    Base.metadata.create_all(bind=engine)
    print("  Database tables created successfully")


def create_admin_user(db: Session) -> User:
    """Create the default admin user if not exists."""
    existing_admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()

    if existing_admin:
        print(f"  Admin user already exists: {ADMIN_EMAIL}")
        return existing_admin

    admin_user = User(
        email=ADMIN_EMAIL,
        hashed_password=get_password_hash(ADMIN_PASSWORD),
        full_name=ADMIN_NAME,
        phone="+1234567890",
        role=UserRole.superadmin,
        is_active=True,
        is_superuser=True,
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    print(f"  Admin user created successfully")
    print(f"  Email:    {ADMIN_EMAIL}")
    print(f"  Password: {ADMIN_PASSWORD}")

    return admin_user


def create_sample_hotel(db: Session) -> Hotel:
    """Create a sample hotel for testing."""
    existing_hotel = db.query(Hotel).filter(Hotel.name == "Grand Hotel Demo").first()

    if existing_hotel:
        print(f"  Sample hotel already exists: {existing_hotel.name}")
        return existing_hotel

    hotel = Hotel(
        name="Grand Hotel Demo",
        address="123 Main Street",
        city="New York",
        state="NY",
        country="USA",
        postal_code="10001",
        phone="+1-555-0100",
        email="info@grandhoteldemo.com",
        website="https://grandhoteldemo.com",
        description="A luxurious demo hotel for testing the system",
        total_floors=3,
        total_rooms=15,
        check_in_time="14:00",
        check_out_time="11:00",
        tax_rate=18,
        is_active=True,
    )

    db.add(hotel)
    db.commit()
    db.refresh(hotel)

    print(f"  Sample hotel created: {hotel.name}")
    return hotel


def create_room_types(db: Session, hotel: Hotel) -> dict:
    """Create room types for the hotel. Returns a dict mapping name -> RoomType."""
    existing = db.query(RoomType).filter(RoomType.hotel_id == hotel.id).count()
    if existing > 0:
        print(f"  Room types already exist: {existing} types")
        types = db.query(RoomType).filter(RoomType.hotel_id == hotel.id).all()
        return {rt.name: rt for rt in types}

    room_types_data = [
        {
            "name": "Standard",
            "description": "Comfortable standard room with essential amenities",
            "base_price": 99.00,
            "extra_bed_price": 25.00,
            "max_occupancy": 2,
            "max_adults": 2,
            "max_children": 1,
            "bed_type": "Double",
            "room_size": 250,
            "amenities": ["WiFi", "AC", "TV", "Mini Bar"],
        },
        {
            "name": "Deluxe",
            "description": "Spacious deluxe room with premium amenities",
            "base_price": 149.00,
            "extra_bed_price": 30.00,
            "max_occupancy": 3,
            "max_adults": 2,
            "max_children": 1,
            "bed_type": "King",
            "room_size": 350,
            "amenities": ["WiFi", "AC", "TV", "Mini Bar", "Balcony", "Room Service"],
        },
        {
            "name": "Suite",
            "description": "Luxurious suite with separate living area",
            "base_price": 249.00,
            "extra_bed_price": 35.00,
            "max_occupancy": 4,
            "max_adults": 3,
            "max_children": 2,
            "bed_type": "King",
            "room_size": 500,
            "amenities": ["WiFi", "AC", "TV", "Mini Bar", "Balcony", "Room Service", "Jacuzzi", "Lounge"],
        },
        {
            "name": "Executive",
            "description": "Executive suite with business facilities",
            "base_price": 399.00,
            "extra_bed_price": 40.00,
            "max_occupancy": 4,
            "max_adults": 3,
            "max_children": 2,
            "bed_type": "King",
            "room_size": 600,
            "amenities": ["WiFi", "AC", "TV", "Mini Bar", "Balcony", "Room Service", "Business Desk", "Lounge"],
        },
        {
            "name": "Presidential",
            "description": "The finest room with all luxury amenities",
            "base_price": 599.00,
            "extra_bed_price": 50.00,
            "max_occupancy": 6,
            "max_adults": 4,
            "max_children": 3,
            "bed_type": "King",
            "room_size": 900,
            "amenities": ["WiFi", "AC", "TV", "Mini Bar", "Balcony", "Room Service", "Jacuzzi", "Lounge", "Private Pool", "Butler"],
        },
    ]

    result = {}
    for data in room_types_data:
        rt = RoomType(hotel_id=hotel.id, is_active=True, **data)
        db.add(rt)
        db.flush()
        result[data["name"]] = rt

    db.commit()
    print(f"  Created {len(result)} room types")
    return result


def create_sample_rooms(db: Session, hotel: Hotel, room_types: dict) -> list:
    """Create sample rooms for the hotel."""
    existing_rooms = db.query(Room).filter(Room.hotel_id == hotel.id).count()

    if existing_rooms > 0:
        print(f"  Rooms already exist for hotel: {existing_rooms} rooms")
        return []

    rooms_data = [
        # Floor 1 - Standard & Deluxe
        {"number": "101", "floor": 1, "type": "Standard"},
        {"number": "102", "floor": 1, "type": "Standard"},
        {"number": "103", "floor": 1, "type": "Standard"},
        {"number": "104", "floor": 1, "type": "Deluxe"},
        {"number": "105", "floor": 1, "type": "Deluxe"},
        # Floor 2 - Deluxe & Suite
        {"number": "201", "floor": 2, "type": "Deluxe"},
        {"number": "202", "floor": 2, "type": "Deluxe"},
        {"number": "203", "floor": 2, "type": "Suite"},
        {"number": "204", "floor": 2, "type": "Suite"},
        {"number": "205", "floor": 2, "type": "Suite"},
        # Floor 3 - Suite, Executive & Presidential
        {"number": "301", "floor": 3, "type": "Suite"},
        {"number": "302", "floor": 3, "type": "Executive"},
        {"number": "303", "floor": 3, "type": "Executive"},
        {"number": "304", "floor": 3, "type": "Presidential"},
        {"number": "305", "floor": 3, "type": "Presidential"},
    ]

    rooms = []
    for room_data in rooms_data:
        rt = room_types[room_data["type"]]
        room = Room(
            hotel_id=hotel.id,
            room_type_id=rt.id,
            room_number=room_data["number"],
            floor=room_data["floor"],
            status=RoomStatus.available,
            is_active=True,
        )
        rooms.append(room)
        db.add(room)

    db.commit()
    print(f"  Created {len(rooms)} sample rooms")
    return rooms


def create_hotel_settings(db: Session, hotel: Hotel) -> HotelSettings:
    """Create default hotel settings."""
    existing = db.query(HotelSettings).filter(
        HotelSettings.hotel_id == hotel.id
    ).first()

    if existing:
        print("  Hotel settings already exist")
        return existing

    settings = HotelSettings(
        hotel_id=hotel.id,
        allow_same_day_booking=True,
        min_advance_booking_days=0,
        max_advance_booking_days=365,
        booking_confirmation_required=False,
        free_cancellation_hours=24,
        cancellation_fee_percent=0,
        require_advance_payment=False,
        advance_payment_percent=0,
        send_booking_confirmation_email=True,
        send_booking_confirmation_whatsapp=True,
        send_check_in_reminder=True,
        reminder_hours_before=24,
        whatsapp_bot_enabled=True,
        ai_assistant_enabled=True,
        ai_auto_suggestions=True,
    )

    db.add(settings)
    db.commit()
    db.refresh(settings)

    print("  Hotel settings created")
    return settings


def create_theme_settings(db: Session, hotel: Hotel) -> ThemeSettings:
    """Create default theme settings."""
    existing = db.query(ThemeSettings).filter(
        ThemeSettings.hotel_id == hotel.id
    ).first()

    if existing:
        print("  Theme settings already exist")
        return existing

    theme = ThemeSettings(
        hotel_id=hotel.id,
        primary_color="#2563eb",
        secondary_color="#64748b",
        accent_color="#f59e0b",
        font_family="Inter, sans-serif",
        brand_name="Grand Hotel Demo",
    )

    db.add(theme)
    db.commit()
    db.refresh(theme)

    print("  Theme settings created")
    return theme


def create_staff_users(db: Session, hotel: Hotel) -> list:
    """Create sample staff users."""
    staff_data = [
        {
            "email": "manager@hotel.com",
            "password": "Manager@123",
            "name": "John Manager",
            "role": UserRole.manager,
        },
        {
            "email": "receptionist@hotel.com",
            "password": "Reception@123",
            "name": "Jane Receptionist",
            "role": UserRole.receptionist,
        },
        {
            "email": "staff@hotel.com",
            "password": "Staff@123",
            "name": "Bob Staff",
            "role": UserRole.staff,
        },
    ]

    users = []
    for data in staff_data:
        existing = db.query(User).filter(User.email == data["email"]).first()
        if existing:
            continue

        user = User(
            email=data["email"],
            hashed_password=get_password_hash(data["password"]),
            full_name=data["name"],
            role=data["role"],
            hotel_id=hotel.id,
            is_active=True,
            is_superuser=False,
        )
        users.append(user)
        db.add(user)

    if users:
        db.commit()
        print(f"  Created {len(users)} staff users")
    else:
        print("  Staff users already exist")

    return users


def seed_database():
    """
    Main function to seed the database with initial data.

    This creates:
    1. Database tables
    2. Admin user (superadmin)
    3. Sample hotel
    4. Room types (Standard, Deluxe, Suite, Executive, Presidential)
    5. Sample rooms (15 rooms across 3 floors)
    6. Staff users
    7. Hotel settings
    8. Theme settings
    """
    print("\n" + "=" * 50)
    print("  HOTEL MANAGEMENT SYSTEM - DATABASE SEEDER")
    print("=" * 50 + "\n")

    # Create tables
    print("--- Creating Tables ---")
    create_tables()

    # Create session
    db = SessionLocal()

    try:
        print("\n--- Creating Users ---")
        admin = create_admin_user(db)

        print("\n--- Creating Sample Hotel ---")
        hotel = create_sample_hotel(db)

        # Associate admin with hotel
        if not admin.hotel_id:
            admin.hotel_id = hotel.id
            db.commit()

        print("\n--- Creating Room Types ---")
        room_types = create_room_types(db, hotel)

        print("\n--- Creating Sample Rooms ---")
        create_sample_rooms(db, hotel, room_types)

        print("\n--- Creating Staff Users ---")
        create_staff_users(db, hotel)

        print("\n--- Creating Hotel Settings ---")
        create_hotel_settings(db, hotel)

        print("\n--- Creating Theme Settings ---")
        create_theme_settings(db, hotel)

        print("\n" + "=" * 50)
        print("  DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("\n  Login Credentials:")
        print("  -----------------------------------------")
        print(f"  Admin:        {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"  Manager:      manager@hotel.com / Manager@123")
        print(f"  Receptionist: receptionist@hotel.com / Reception@123")
        print(f"  Staff:        staff@hotel.com / Staff@123")
        print("  -----------------------------------------")
        print(f"\n  Hotel: {hotel.name}")
        print(f"  Room Types: {', '.join(room_types.keys())}")
        print(f"  Total Rooms: 15\n")

    except Exception as e:
        print(f"\n  Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
