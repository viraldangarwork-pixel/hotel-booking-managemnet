# Hotel Management System - Application Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Vue.js)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Login     │  │  Dashboard  │  │   Rooms     │  │  Bookings   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Guests    │  │    Chat     │  │  Settings   │  │   Reports   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             BACKEND (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         API Endpoints                            │   │
│  │  /auth  /users  /hotels  /rooms  /bookings  /guests  /payments  │   │
│  │  /chat  /dashboard  /settings                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                          Services                                │   │
│  │  BookingService  RoomService  GuestService  PaymentService      │   │
│  │  WhatsAppService  AIService  NotificationService                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ SQLAlchemy ORM
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATABASE (PostgreSQL)                         │
│  users | hotels | rooms | bookings | guests | payments | chat_sessions │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Complete Application Flows

### 1. Authentication Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│  User    │         │ Frontend │         │ Backend  │         │ Database │
└────┬─────┘         └────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │                    │
     │ 1. Enter email     │                    │                    │
     │    & password      │                    │                    │
     │───────────────────>│                    │                    │
     │                    │                    │                    │
     │                    │ 2. POST /auth/login│                    │
     │                    │───────────────────>│                    │
     │                    │                    │                    │
     │                    │                    │ 3. Validate user   │
     │                    │                    │───────────────────>│
     │                    │                    │                    │
     │                    │                    │ 4. User data       │
     │                    │                    │<───────────────────│
     │                    │                    │                    │
     │                    │                    │ 5. Verify password │
     │                    │                    │    Generate JWT    │
     │                    │                    │                    │
     │                    │ 6. Return tokens   │                    │
     │                    │<───────────────────│                    │
     │                    │                    │                    │
     │                    │ 7. Store token     │                    │
     │                    │    in localStorage │                    │
     │                    │                    │                    │
     │ 8. Redirect to     │                    │                    │
     │    Dashboard       │                    │                    │
     │<───────────────────│                    │                    │
     │                    │                    │                    │
```

**Steps:**
1. User enters `admin@hotel.com` and `Admin@123` on login page
2. Frontend sends POST request to `/api/v1/auth/login`
3. Backend queries database for user
4. Database returns user record
5. Backend verifies password hash and generates JWT token
6. Backend returns access_token and refresh_token
7. Frontend stores tokens in localStorage/Pinia store
8. User is redirected to Dashboard

---

### 2. Booking Flow (Complete Journey)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        BOOKING LIFECYCLE                                 │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
  │ PENDING  │────>│CONFIRMED │────>│ CHECKED  │────>│ CHECKED  │
  │          │     │          │     │   IN     │     │   OUT    │
  └──────────┘     └──────────┘     └──────────┘     └──────────┘
       │                │                                  │
       │                │                                  │
       ▼                ▼                                  ▼
  ┌──────────┐     ┌──────────┐                      ┌──────────┐
  │CANCELLED │     │ NO SHOW  │                      │COMPLETED │
  └──────────┘     └──────────┘                      └──────────┘
```

#### Step-by-Step Booking Process:

**A. Create Booking**
```
User Action: Click "New Booking" → Select dates → Select room → Enter guest details

API Flow:
1. GET  /api/v1/rooms/available?check_in=2024-01-15&check_out=2024-01-18
2. POST /api/v1/guests          (Create or find guest)
3. POST /api/v1/bookings        (Create booking)
4. POST /api/v1/payments        (Record payment if any)

Backend Logic:
├── BookingService.check_room_availability()
├── BookingService.calculate_booking_totals()
├── Create Booking record (status: PENDING)
├── Update Room status to RESERVED
├── Send confirmation email via NotificationService
└── Send WhatsApp confirmation via WhatsAppService
```

**B. Check-In Process**
```
User Action: Click "Check In" on booking

API Flow:
1. PUT /api/v1/bookings/{id}/check-in

Backend Logic:
├── Validate booking status is CONFIRMED
├── Update booking status to CHECKED_IN
├── Update actual_check_in timestamp
├── Update Room status to OCCUPIED
├── Generate room key card (if integrated)
└── Send welcome message via WhatsApp
```

**C. Check-Out Process**
```
User Action: Click "Check Out" on booking

API Flow:
1. GET  /api/v1/payments/booking/{id}/summary
2. POST /api/v1/payments                      (Final payment)
3. PUT  /api/v1/bookings/{id}/check-out

Backend Logic:
├── Calculate final charges (room + extras)
├── Process final payment
├── Update booking status to CHECKED_OUT
├── Update actual_check_out timestamp
├── Update Room status to DIRTY (needs cleaning)
├── Generate invoice via PaymentService
└── Send thank you message + invoice via email
```

---

### 3. Room Management Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ROOM STATUS CYCLE                                │
└─────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────┐
                              │  AVAILABLE   │◄─────────────────┐
                              └──────┬───────┘                  │
                                     │                          │
                           Booking Created                 Cleaning Done
                                     │                          │
                                     ▼                          │
                              ┌──────────────┐           ┌──────────────┐
                              │   RESERVED   │           │    DIRTY     │
                              └──────┬───────┘           └──────┬───────┘
                                     │                          ▲
                              Guest Checks In                   │
                                     │                    Guest Checks Out
                                     ▼                          │
                              ┌──────────────┐                  │
                              │   OCCUPIED   │──────────────────┘
                              └──────────────┘

                              ┌──────────────┐
                              │ MAINTENANCE  │ (Can be set from any status)
                              └──────────────┘
```

**API Endpoints:**
```
GET    /api/v1/rooms                    # List all rooms
GET    /api/v1/rooms/{id}               # Get room details
GET    /api/v1/rooms/available          # Get available rooms for dates
PUT    /api/v1/rooms/{id}/status        # Update room status
GET    /api/v1/rooms/floor/{floor}      # Get rooms by floor
GET    /api/v1/rooms/status-counts      # Dashboard statistics
```

---

### 4. Guest CRM Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GUEST LIFECYCLE                                  │
└─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐                                      ┌─────────────┐
  │   NEW GUEST │                                      │  VIP GUEST  │
  │  (1st Visit)│                                      │ (Loyalty)   │
  └──────┬──────┘                                      └──────▲──────┘
         │                                                    │
         │                                             Marked as VIP
         │                                             (Manual or Auto)
         ▼                                                    │
  ┌─────────────┐     ┌─────────────┐     ┌─────────────────────────────┐
  │   Makes     │────>│  Booking    │────>│   Guest Profile Updated     │
  │   Booking   │     │  Completed  │     │   - Total stays count       │
  └─────────────┘     └─────────────┘     │   - Total spend             │
                                          │   - Preferences recorded    │
                                          │   - Special requests saved  │
                                          └─────────────────────────────┘
```

**CRM Features:**
- Guest search by name, email, phone
- View complete booking history
- Track total spend and visits
- Store preferences (room type, floor, dietary)
- VIP status management
- Notes and special requests

---

### 5. Chat & AI Assistant Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CHAT SYSTEM ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐              ┌─────────────┐              ┌─────────────┐
    │   GUEST     │              │   STAFF     │              │  AI ENGINE  │
    │  (WhatsApp) │              │  (Dashboard)│              │  (OpenAI)   │
    └──────┬──────┘              └──────┬──────┘              └──────┬──────┘
           │                            │                            │
           │ 1. Send message            │                            │
           │ via WhatsApp               │                            │
           │                            │                            │
           ▼                            │                            │
    ┌─────────────┐                     │                            │
    │  WhatsApp   │                     │                            │
    │  Business   │                     │                            │
    │    API      │                     │                            │
    └──────┬──────┘                     │                            │
           │                            │                            │
           │ 2. Webhook to backend      │                            │
           │                            │                            │
           ▼                            ▼                            │
    ┌─────────────────────────────────────────────────┐              │
    │                   BACKEND                        │              │
    │  ┌─────────────────────────────────────────┐    │              │
    │  │          WhatsAppService                 │    │              │
    │  │  - Receive incoming message              │    │              │
    │  │  - Parse message content                 │    │              │
    │  │  - Route to AI or Staff                  │    │              │
    │  └─────────────────────────────────────────┘    │              │
    │                      │                          │              │
    │                      ▼                          │              │
    │  ┌─────────────────────────────────────────┐    │              │
    │  │            AIService                     │◄───────────────────
    │  │  - Analyze intent                        │    │
    │  │  - Query booking info                    │    │
    │  │  - Generate response                     │    │
    │  └─────────────────────────────────────────┘    │
    │                      │                          │
    │                      ▼                          │
    │  ┌─────────────────────────────────────────┐    │
    │  │       Chat Session Storage               │    │
    │  │  - Save conversation history             │    │
    │  │  - Track session context                 │    │
    │  └─────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────┘
```

**AI Capabilities:**
- Booking inquiries ("What's my reservation status?")
- Room availability checks ("Any rooms available next week?")
- FAQ responses ("What time is check-in?")
- Complaint handling (escalate to staff)
- Service requests ("I need extra towels")

---

### 6. Dashboard Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       DASHBOARD VIEW                                     │
└─────────────────────────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────────────────┐
   │  GET /api/v1/dashboard/stats                                        │
   │                                                                     │
   │  Returns:                                                           │
   │  {                                                                  │
   │    "total_rooms": 20,                                              │
   │    "occupied_rooms": 12,                                           │
   │    "available_rooms": 6,                                           │
   │    "maintenance_rooms": 2,                                         │
   │    "occupancy_rate": 60.0,                                         │
   │    "today_check_ins": 5,                                           │
   │    "today_check_outs": 3,                                          │
   │    "pending_bookings": 8,                                          │
   │    "revenue_today": 2450.00,                                       │
   │    "revenue_month": 45600.00                                       │
   │  }                                                                  │
   └─────────────────────────────────────────────────────────────────────┘

   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────┐
   │   Stats Card   │  │   Stats Card   │  │   Stats Card   │  │  Card  │
   │   Occupancy    │  │  Today Check   │  │    Revenue     │  │ Rooms  │
   │     60%        │  │   Ins: 5       │  │   $2,450       │  │  20    │
   └────────────────┘  └────────────────┘  └────────────────┘  └────────┘

   ┌─────────────────────────────┐  ┌─────────────────────────────────────┐
   │      Today's Bookings       │  │         AI Insights                  │
   │  ┌─────────────────────────┐│  │  ┌─────────────────────────────────┐│
   │  │ #BK001 - John Doe       ││  │  │ "Consider offering weekend      ││
   │  │ Room 101 - Check In 2PM ││  │  │  discounts - occupancy drops    ││
   │  ├─────────────────────────┤│  │  │  30% on Saturdays"              ││
   │  │ #BK002 - Jane Smith     ││  │  ├─────────────────────────────────┤│
   │  │ Room 203 - Check Out    ││  │  │ "5 guests have birthdays this   ││
   │  └─────────────────────────┘│  │  │  month - opportunity for VIP    ││
   └─────────────────────────────┘  │  │  treatment"                     ││
                                    │  └─────────────────────────────────┘│
                                    └─────────────────────────────────────┘
```

---

### 7. Theme System Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THEME CONFIGURATION FLOW                              │
└─────────────────────────────────────────────────────────────────────────┘

  .env File                    Tailwind Config               CSS Variables
  ┌──────────────┐            ┌──────────────┐             ┌──────────────┐
  │VITE_PRIMARY  │            │ theme: {     │             │ :root {      │
  │  _COLOR=     │───────────>│   colors: {  │────────────>│   --primary: │
  │  #3B82F6     │            │     primary  │             │     #3B82F6  │
  │              │            │   }          │             │ }            │
  │VITE_DARK_MODE│            │ }            │             │              │
  │  =true       │            └──────────────┘             │ .dark {      │
  └──────────────┘                                         │   --bg:      │
                                                           │     #1F2937  │
                                                           │ }            │
                                                           └──────────────┘
                                                                  │
                                                                  ▼
                                                           ┌──────────────┐
                                                           │  Components  │
                                                           │  use CSS     │
                                                           │  variables   │
                                                           │              │
                                                           │ bg-primary   │
                                                           │ text-surface │
                                                           └──────────────┘
```

**Theme Toggle (Pinia Store):**
```javascript
// User clicks dark mode toggle
themeStore.toggleDarkMode()
  │
  ├── Updates localStorage('darkMode')
  ├── Adds/removes 'dark' class on <html>
  └── CSS variables automatically switch
```

---

## API Reference Quick Guide

| Action | Method | Endpoint | Auth Required |
|--------|--------|----------|---------------|
| Login | POST | `/api/v1/auth/login` | No |
| Get Dashboard | GET | `/api/v1/dashboard/stats` | Yes |
| List Rooms | GET | `/api/v1/rooms` | Yes |
| Create Booking | POST | `/api/v1/bookings` | Yes |
| Check In | PUT | `/api/v1/bookings/{id}/check-in` | Yes |
| Check Out | PUT | `/api/v1/bookings/{id}/check-out` | Yes |
| List Guests | GET | `/api/v1/guests` | Yes |
| Send WhatsApp | POST | `/api/v1/chat/whatsapp/send` | Yes |
| AI Chat | POST | `/api/v1/chat/ai/message` | Yes |

---

## Data Models Relationship

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATABASE SCHEMA RELATIONSHIPS                     │
└─────────────────────────────────────────────────────────────────────────┘

                              ┌──────────┐
                              │  Hotel   │
                              └────┬─────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
    ┌──────────┐            ┌──────────┐            ┌──────────┐
    │   Room   │            │   User   │            │ Settings │
    └────┬─────┘            └──────────┘            └──────────┘
         │
         │
         ▼
    ┌──────────┐            ┌──────────┐
    │ Booking  │◄──────────>│  Guest   │
    └────┬─────┘            └──────────┘
         │
         │
         ▼
    ┌──────────┐            ┌──────────┐
    │ Payment  │            │  Chat    │
    └──────────┘            │ Session  │
                            └──────────┘
```

---

## Quick Start Commands

```bash
# 1. Clone and setup
git clone <repo>
cd hotel-booking-management

# 2. Start backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python scripts/init_db.py  # Creates admin user & sample data
uvicorn app.main:app --reload

# 3. Start frontend (new terminal)
cd frontend
npm install
npm run dev

# 4. Open browser
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs

# 5. Login with:
# Email: admin@hotel.com
# Password: Admin@123
```
