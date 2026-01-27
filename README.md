# Hotel Booking Management System

A comprehensive, AI-powered Hotel Management System with WhatsApp integration, CRM, and configurable theming.

## Project Structure

```
hotel-booking-management/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configurations
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── alembic/            # Database migrations
│   └── tests/              # Backend tests
├── frontend/               # Vue.js Frontend
│   ├── src/
│   │   ├── assets/         # Static assets & styles
│   │   ├── components/     # Vue components
│   │   ├── composables/    # Vue composables
│   │   ├── layouts/        # Layout components
│   │   ├── router/         # Vue Router
│   │   ├── stores/         # Pinia stores
│   │   ├── views/          # Page views
│   │   └── utils/          # Frontend utilities
│   └── public/             # Public assets
└── docker-compose.yml      # Docker orchestration
```

## Features

- **Hotel & Room Management**: Real-time room status, floor-wise views
- **Booking Management**: Online & WhatsApp bookings with full lifecycle
- **Guest CRM**: Complete guest profiles with booking history
- **WhatsApp Chatbot**: Official WhatsApp Business API integration
- **AI Assistant**: Smart replies, predictions, and admin queries
- **Billing & Payments**: Invoicing, payment tracking, discounts
- **Theme System**: Configurable via environment variables
- **Dark/Light Mode**: System-wide theme switching

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Auth**: JWT with role-based access
- **Real-time**: WebSockets

### Frontend
- **Framework**: Vue.js 3 (Composition API)
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios
- **Styling**: CSS Variables + Tailwind CSS

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd hotel-booking-management
```

2. Start with Docker:
```bash
docker-compose up -d
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

See `.env.example` files in both `backend/` and `frontend/` directories.

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT License
