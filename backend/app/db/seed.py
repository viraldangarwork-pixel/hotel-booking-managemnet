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
from app.models.settings import SystemSettings


# ============================================
# DEFAULT ADMIN CREDENTIALS
# ============================================
ADMIN_EMAIL = "admin@hotel.com"
ADMIN_PASSWORD = "Admin@123"
ADMIN_NAME = "System Administrator"
# ============================================


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def create_admin_user(db: Session) -> User:
    """Create the default admin user if not exists."""
    existing_admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()

    if existing_admin:
        print(f"✓ Admin user already exists: {ADMIN_EMAIL}")
        return existing_admin

    admin_user = User(
        email=ADMIN_EMAIL,
        hashed_password=get_password_hash(ADMIN_PASSWORD),
        full_name=ADMIN_NAME,
        phone="+1234567890",
        role=UserRole.SUPERADMIN,
        is_active=True,
        is_superuser=True,
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    print(f"✓ Admin user created successfully")
    print(f"  Email:    {ADMIN_EMAIL}")
    print(f"  Password: {ADMIN_PASSWORD}")

    return admin_user


def create_sample_hotel(db: Session) -> Hotel:
    """Create a sample hotel for testing."""
    existing_hotel = db.query(Hotel).filter(Hotel.code == "DEMO001").first()

    if existing_hotel:
        print(f"✓ Sample hotel already exists: {existing_hotel.name}")
        return existing_hotel

    hotel = Hotel(
        name="Grand Hotel Demo",
        code="DEMO001",
        address="123 Main Street",
        city="New York",
        state="NY",
        country="USA",
        postal_code="10001",
        phone="+1-555-0100",
        email="info@grandhoteldemo.com",
        website="https://grandhoteldemo.com",
        description="A luxurious demo hotel for testing the system",
        star_rating=5,
        total_rooms=20,
        is_active=True,
    )

    db.add(hotel)
    db.commit()
    db.refresh(hotel)

    print(f"✓ Sample hotel created: {hotel.name}")
    return hotel


def create_sample_rooms(db: Session, hotel: Hotel) -> list:
    """Create sample rooms for the hotel."""
    existing_rooms = db.query(Room).filter(Room.hotel_id == hotel.id).count()

    if existing_rooms > 0:
        print(f"✓ Rooms already exist for hotel: {existing_rooms} rooms")
        return []

    rooms_data = [
        # Standard Rooms (Floor 1)
        {"number": "101", "floor": 1, "type": RoomType.STANDARD, "price": 99.00},
        {"number": "102", "floor": 1, "type": RoomType.STANDARD, "price": 99.00},
        {"number": "103", "floor": 1, "type": RoomType.STANDARD, "price": 99.00},
        {"number": "104", "floor": 1, "type": RoomType.DELUXE, "price": 149.00},
        {"number": "105", "floor": 1, "type": RoomType.DELUXE, "price": 149.00},
        # Deluxe Rooms (Floor 2)
        {"number": "201", "floor": 2, "type": RoomType.DELUXE, "price": 149.00},
        {"number": "202", "floor": 2, "type": RoomType.DELUXE, "price": 149.00},
        {"number": "203", "floor": 2, "type": RoomType.SUITE, "price": 249.00},
        {"number": "204", "floor": 2, "type": RoomType.SUITE, "price": 249.00},
        {"number": "205", "floor": 2, "type": RoomType.SUITE, "price": 249.00},
        # Suites (Floor 3)
        {"number": "301", "floor": 3, "type": RoomType.SUITE, "price": 299.00},
        {"number": "302", "floor": 3, "type": RoomType.EXECUTIVE, "price": 399.00},
        {"number": "303", "floor": 3, "type": RoomType.EXECUTIVE, "price": 399.00},
        {"number": "304", "floor": 3, "type": RoomType.PRESIDENTIAL, "price": 599.00},
        {"number": "305", "floor": 3, "type": RoomType.PRESIDENTIAL, "price": 599.00},
    ]

    rooms = []
    for room_data in rooms_data:
        room = Room(
            hotel_id=hotel.id,
            room_number=room_data["number"],
            floor=room_data["floor"],
            room_type=room_data["type"],
            base_price=room_data["price"],
            max_occupancy=2 if room_data["type"] in [RoomType.STANDARD, RoomType.DELUXE] else 4,
            status=RoomStatus.AVAILABLE,
            description=f"{room_data['type'].value.title()} room on floor {room_data['floor']}",
            is_active=True,
        )
        rooms.append(room)
        db.add(room)

    db.commit()
    print(f"✓ Created {len(rooms)} sample rooms")
    return rooms


def create_system_settings(db: Session, hotel: Hotel) -> SystemSettings:
    """Create default system settings."""
    existing_settings = db.query(SystemSettings).filter(
        SystemSettings.hotel_id == hotel.id
    ).first()

    if existing_settings:
        print("✓ System settings already exist")
        return existing_settings

    settings = SystemSettings(
        hotel_id=hotel.id,
        settings_data={
            "check_in_time": "14:00",
            "check_out_time": "11:00",
            "currency": "USD",
            "timezone": "America/New_York",
            "date_format": "MM/DD/YYYY",
            "tax_rate": 10.0,
            "cancellation_policy": "Free cancellation up to 24 hours before check-in",
            "whatsapp_enabled": True,
            "ai_assistant_enabled": True,
            "email_notifications": True,
        }
    )

    db.add(settings)
    db.commit()
    db.refresh(settings)

    print("✓ System settings created")
    return settings


def create_staff_users(db: Session, hotel: Hotel) -> list:
    """Create sample staff users."""
    staff_data = [
        {
            "email": "manager@hotel.com",
            "password": "Manager@123",
            "name": "John Manager",
            "role": UserRole.MANAGER,
        },
        {
            "email": "receptionist@hotel.com",
            "password": "Reception@123",
            "name": "Jane Receptionist",
            "role": UserRole.RECEPTIONIST,
        },
        {
            "email": "staff@hotel.com",
            "password": "Staff@123",
            "name": "Bob Staff",
            "role": UserRole.STAFF,
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
        print(f"✓ Created {len(users)} staff users")
    else:
        print("✓ Staff users already exist")

    return users


def seed_database():
    """
    Main function to seed the database with initial data.

    This creates:
    1. Database tables
    2. Admin user (superadmin)
    3. Sample hotel
    4. Sample rooms
    5. Staff users
    6. System settings
    """
    print("\n" + "=" * 50)
    print("  HOTEL MANAGEMENT SYSTEM - DATABASE SEEDER")
    print("=" * 50 + "\n")

    # Create tables
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

        print("\n--- Creating Sample Rooms ---")
        create_sample_rooms(db, hotel)

        print("\n--- Creating Staff Users ---")
        create_staff_users(db, hotel)

        print("\n--- Creating System Settings ---")
        create_system_settings(db, hotel)

        print("\n" + "=" * 50)
        print("  DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("\n  Login Credentials:")
        print("  ─────────────────────────────────────────")
        print(f"  Admin:        {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"  Manager:      manager@hotel.com / Manager@123")
        print(f"  Receptionist: receptionist@hotel.com / Reception@123")
        print(f"  Staff:        staff@hotel.com / Staff@123")
        print("  ─────────────────────────────────────────\n")

    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
