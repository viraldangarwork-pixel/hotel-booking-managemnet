"""Shared fixtures for backend API tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.main import app
from app.models.user import User, UserRole
from app.models.hotel import Hotel
from app.models.room import Room, RoomType, RoomStatus
from app.models.guest import Guest
from app.models.booking import Booking, BookingStatus, BookingSource

# In-memory SQLite for fast isolated tests
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """FastAPI test client with DB override."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def hotel(db):
    """Create a test hotel."""
    h = Hotel(
        name="Test Hotel",
        address="123 Test St",
        city="Test City",
        state="TS",
        country="Testland",
        postal_code="12345",
        phone="+1234567890",
        email="test@hotel.com",
        total_floors=2,
        total_rooms=5,
        check_in_time="14:00",
        check_out_time="11:00",
        tax_rate=18,
        is_active=True,
    )
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


@pytest.fixture
def admin_user(db, hotel):
    """Create an admin user and return (user, plain_password)."""
    password = "Admin@123"
    user = User(
        email="admin@test.com",
        hashed_password=get_password_hash(password),
        full_name="Test Admin",
        phone="+1111111111",
        role=UserRole.superadmin,
        hotel_id=hotel.id,
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, password


@pytest.fixture
def auth_headers(client, admin_user):
    """Get auth headers by logging in the admin user."""
    user, password = admin_user
    response = client.post("/api/v1/auth/login", json={
        "email": user.email,
        "password": password,
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def room_type(db, hotel):
    """Create a test room type."""
    rt = RoomType(
        hotel_id=hotel.id,
        name="Standard",
        description="Standard room",
        base_price=100.00,
        extra_bed_price=25.00,
        max_occupancy=2,
        max_adults=2,
        max_children=1,
        bed_type="Double",
        room_size=250,
        amenities=["WiFi", "AC"],
        is_active=True,
    )
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


@pytest.fixture
def room(db, hotel, room_type):
    """Create a test room."""
    r = Room(
        hotel_id=hotel.id,
        room_type_id=room_type.id,
        room_number="101",
        floor=1,
        status=RoomStatus.available,
        is_active=True,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@pytest.fixture
def guest(db, hotel):
    """Create a test guest."""
    g = Guest(
        hotel_id=hotel.id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+9876543210",
        address="456 Guest Lane",
        city="Guest City",
        country="India",
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return g
