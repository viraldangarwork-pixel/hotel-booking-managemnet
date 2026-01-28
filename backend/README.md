# Hotel Management System - Backend

FastAPI backend for the Hotel Management System.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **JWT** - Authentication

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/     # API route handlers
│   │           ├── auth.py
│   │           ├── bookings.py
│   │           ├── chat.py
│   │           ├── dashboard.py
│   │           ├── guests.py
│   │           ├── hotels.py
│   │           ├── payments.py
│   │           ├── rooms.py
│   │           ├── settings.py
│   │           └── users.py
│   ├── core/
│   │   ├── config.py          # App configuration
│   │   ├── database.py        # Database setup
│   │   └── security.py        # Auth utilities
│   ├── models/                # SQLAlchemy models
│   │   ├── booking.py
│   │   ├── chat.py
│   │   ├── guest.py
│   │   ├── hotel.py
│   │   ├── payment.py
│   │   ├── room.py
│   │   ├── settings.py
│   │   └── user.py
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   │   ├── ai_service.py
│   │   ├── booking_service.py
│   │   ├── guest_service.py
│   │   ├── notification_service.py
│   │   ├── payment_service.py
│   │   ├── room_service.py
│   │   └── whatsapp_service.py
│   ├── utils/                 # Helpers
│   │   ├── helpers.py
│   │   ├── pagination.py
│   │   └── validators.py
│   └── main.py               # App entry point
├── alembic/                  # Migrations
├── tests/                    # Test files
├── requirements.txt
└── Dockerfile
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis (optional, for caching)

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings
```

### Database Setup

```bash
# Create database
createdb hotel_management

# Run migrations
alembic upgrade head
```

### Running the Server

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Hotels
- `GET /api/v1/hotels` - List hotels
- `POST /api/v1/hotels` - Create hotel
- `GET /api/v1/hotels/{id}` - Get hotel
- `PUT /api/v1/hotels/{id}` - Update hotel

### Rooms
- `GET /api/v1/rooms` - List rooms
- `GET /api/v1/rooms/availability` - Check availability
- `GET /api/v1/rooms/types` - List room types
- `POST /api/v1/rooms` - Create room
- `PUT /api/v1/rooms/{id}/status` - Update status

### Bookings
- `GET /api/v1/bookings` - List bookings
- `GET /api/v1/bookings/today` - Today's schedule
- `POST /api/v1/bookings` - Create booking
- `POST /api/v1/bookings/{id}/check-in` - Check-in
- `POST /api/v1/bookings/{id}/check-out` - Check-out
- `POST /api/v1/bookings/{id}/cancel` - Cancel

### Guests
- `GET /api/v1/guests` - List guests
- `GET /api/v1/guests/search` - Search
- `POST /api/v1/guests` - Create guest
- `PUT /api/v1/guests/{id}/vip` - Toggle VIP

### Payments
- `GET /api/v1/payments` - List payments
- `POST /api/v1/payments` - Record payment
- `POST /api/v1/payments/{id}/refund` - Process refund

### Dashboard
- `GET /api/v1/dashboard/stats` - Statistics
- `GET /api/v1/dashboard/occupancy` - Occupancy trend
- `GET /api/v1/dashboard/revenue` - Revenue trend
- `GET /api/v1/dashboard/insights` - AI insights

### Chat
- `GET /api/v1/chat/whatsapp` - List WhatsApp chats
- `POST /api/v1/chat/whatsapp/webhook` - WhatsApp webhook
- `POST /api/v1/chat/ai/sessions` - Create AI session
- `POST /api/v1/chat/ai/sessions/{id}/message` - Send message

### Settings
- `GET /api/v1/settings/theme/{hotel_id}` - Get theme
- `PUT /api/v1/settings/theme/{hotel_id}` - Update theme
- `GET /api/v1/settings/hotel/{hotel_id}` - Get settings
- `PUT /api/v1/settings/hotel/{hotel_id}` - Update settings

## Environment Variables

```env
# Application
APP_NAME=Hotel Management System
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key
API_V1_PREFIX=/api/v1

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/hotel_management
DATABASE_ECHO=false

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# WhatsApp Business API
WHATSAPP_API_TOKEN=your-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-verify-token

# OpenAI
OPENAI_API_KEY=your-api-key
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email
SMTP_PASSWORD=your-password
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_bookings.py
```

## Code Quality

```bash
# Format code
black app/
isort app/

# Lint
flake8 app/
mypy app/
```

## Services

### BookingService
Handles booking lifecycle: creation, check-in, check-out, cancellation, pricing calculations.

### RoomService
Manages rooms and room types, availability checking, status updates.

### GuestService
CRM operations: guest profiles, search, VIP management, preferences.

### PaymentService
Payment processing, refunds, invoice generation, revenue reporting.

### WhatsAppService
WhatsApp Business API integration, message sending, webhook handling.

### AIService
AI assistant operations, intent analysis, context-aware responses.

### NotificationService
Email notifications for bookings, reminders, and staff alerts.

## License

MIT
