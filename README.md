# Hotel Booking Management System

A comprehensive, AI-powered Hotel Management System with WhatsApp integration, CRM, and configurable theming.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Development](#development)
- [Deployment](#deployment)

## Features

### Core Modules

| Module | Description |
|--------|-------------|
| **Hotel Management** | Multi-property support, hotel settings, branding |
| **Room Management** | Room types, floor-wise view, real-time status |
| **Booking Management** | Full lifecycle: Inquiry → Confirmation → Check-in → Check-out |
| **Guest CRM** | Profiles, preferences, booking history, VIP tagging |
| **Billing & Payments** | Invoicing, multiple payment methods, GST support |
| **WhatsApp Integration** | Official Business API, chatbot, human handover |
| **AI Assistant** | Smart queries, occupancy predictions, insights |

### Frontend Features

- **Configurable Theme System** - Customize colors, fonts, spacing via environment variables
- **Dark/Light Mode** - System preference detection with manual toggle
- **Responsive Design** - Mobile-first approach with Tailwind CSS
- **Real-time Updates** - WebSocket support for live data

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | Web framework |
| PostgreSQL | Database |
| SQLAlchemy | ORM |
| Alembic | Migrations |
| Pydantic | Validation |
| JWT | Authentication |
| Redis | Caching (optional) |

### Frontend
| Technology | Purpose |
|------------|---------|
| Vue.js 3 | UI Framework |
| Vite | Build tool |
| Pinia | State management |
| Vue Router | Routing |
| Tailwind CSS | Styling |
| Axios | HTTP client |

## Project Structure

```
hotel-booking-management/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # REST API endpoints
│   │   ├── core/               # Config, DB, Security
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic
│   │   └── utils/              # Helper utilities
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Test files
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── assets/styles/      # CSS with theme variables
│   │   ├── components/         # Vue components
│   │   ├── composables/        # Vue composables
│   │   ├── layouts/            # Layout templates
│   │   ├── router/             # Vue Router config
│   │   ├── stores/             # Pinia stores
│   │   ├── views/              # Page components
│   │   └── utils/              # Helpers & formatters
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd hotel-booking-management

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis (optional)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

## Configuration

### Backend Environment Variables

```env
# Application
APP_NAME=Hotel Management System
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/hotel_db

# JWT
JWT_SECRET_KEY=your-jwt-secret
ACCESS_TOKEN_EXPIRE_MINUTES=30

# WhatsApp (optional)
WHATSAPP_API_TOKEN=your-token
WHATSAPP_PHONE_NUMBER_ID=your-id

# OpenAI (optional)
OPENAI_API_KEY=your-key
```

### Frontend Environment Variables

```env
# API
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_HOTEL_ID=1

# Theme
VITE_PRIMARY_COLOR=#2563eb
VITE_FONT_FAMILY=Inter, sans-serif
VITE_BORDER_RADIUS=8px

# Features
VITE_ENABLE_WHATSAPP=true
VITE_ENABLE_AI_ASSISTANT=true
VITE_ENABLE_DARK_MODE=true
```

## API Documentation

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login` | POST | User login |
| `/api/v1/auth/register` | POST | User registration |
| `/api/v1/auth/refresh` | POST | Refresh token |
| `/api/v1/auth/me` | GET | Current user info |

### Rooms
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/rooms` | GET | List rooms |
| `/api/v1/rooms/availability` | GET | Check availability |
| `/api/v1/rooms/{id}` | GET | Get room details |
| `/api/v1/rooms/{id}/status` | PUT | Update room status |

### Bookings
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/bookings` | GET | List bookings |
| `/api/v1/bookings` | POST | Create booking |
| `/api/v1/bookings/{id}/check-in` | POST | Process check-in |
| `/api/v1/bookings/{id}/check-out` | POST | Process check-out |

### Guests
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/guests` | GET | List guests |
| `/api/v1/guests/search` | GET | Search guests |
| `/api/v1/guests/{id}/vip` | PUT | Toggle VIP status |

### Dashboard
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/dashboard/stats` | GET | Dashboard statistics |
| `/api/v1/dashboard/occupancy` | GET | Occupancy trend |
| `/api/v1/dashboard/revenue` | GET | Revenue trend |
| `/api/v1/dashboard/insights` | GET | AI insights |

Full API documentation available at `/docs` (Swagger) or `/redoc` (ReDoc).

## Database Schema

### Core Tables
- `hotels` - Hotel properties
- `room_types` - Room categories (Deluxe, Suite, etc.)
- `rooms` - Individual rooms
- `guests` - Guest profiles (CRM)
- `bookings` - Reservations
- `payments` - Payment transactions

### Supporting Tables
- `users` - Staff accounts
- `whatsapp_chats` - WhatsApp conversations
- `whatsapp_messages` - Chat messages
- `ai_chat_sessions` - AI assistant sessions
- `theme_settings` - UI theme configuration
- `hotel_settings` - Hotel-specific settings

## Development

### Code Style

**Backend:**
```bash
# Format code
black app/
isort app/

# Lint
flake8 app/
mypy app/
```

**Frontend:**
```bash
# Format code
npm run format

# Lint
npm run lint
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

### Creating Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Deployment

### Production Build

**Backend:**
```bash
# Use production settings
export APP_ENV=production
export DEBUG=false

# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Frontend:**
```bash
npm run build
# Serve dist/ folder with nginx or similar
```

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## License

MIT License - see LICENSE file for details.

## Support

For issues and feature requests, please use the GitHub Issues page.
