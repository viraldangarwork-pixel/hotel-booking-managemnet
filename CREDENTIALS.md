# Hotel Management System - Default Credentials

## Admin Login

| Role | Email | Password |
|------|-------|----------|
| **Super Admin** | `admin@hotel.com` | `Admin@123` |
| Manager | `manager@hotel.com` | `Manager@123` |
| Receptionist | `receptionist@hotel.com` | `Reception@123` |
| Staff | `staff@hotel.com` | `Staff@123` |

---

## Quick Start

### 1. Start the Backend
```bash
cd backend
pip install -r requirements.txt
python scripts/init_db.py   # Initialize database with default users
uvicorn app.main:app --reload
```

### 2. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Login
- Open `http://localhost:5173` in your browser
- Use admin credentials: `admin@hotel.com` / `Admin@123`

---

## Role Permissions

| Permission | Super Admin | Manager | Receptionist | Staff |
|------------|-------------|---------|--------------|-------|
| View Dashboard | ✅ | ✅ | ✅ | ✅ |
| Manage Bookings | ✅ | ✅ | ✅ | ❌ |
| Check-in/Check-out | ✅ | ✅ | ✅ | ❌ |
| Manage Rooms | ✅ | ✅ | ❌ | ❌ |
| Manage Guests (CRM) | ✅ | ✅ | ✅ | ❌ |
| View Reports | ✅ | ✅ | ❌ | ❌ |
| Manage Staff | ✅ | ❌ | ❌ | ❌ |
| System Settings | ✅ | ❌ | ❌ | ❌ |
| AI Assistant | ✅ | ✅ | ✅ | ✅ |
| WhatsApp Chat | ✅ | ✅ | ✅ | ❌ |
