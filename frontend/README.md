# Hotel Management System - Frontend

Vue.js 3 frontend for the Hotel Management System.

## Tech Stack

- **Vue.js 3** - Progressive JavaScript framework (Composition API)
- **Vite** - Next-generation build tool
- **Pinia** - State management
- **Vue Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client

## Features

- **Configurable Theme System** - CSS variables for colors, fonts, spacing
- **Dark/Light Mode** - System preference detection with manual toggle
- **Responsive Design** - Mobile-first approach
- **Real-time Updates** - WebSocket support

## Project Structure

```
frontend/
├── public/                   # Static assets
├── src/
│   ├── assets/
│   │   └── styles/
│   │       └── main.css     # Theme CSS variables
│   ├── components/
│   │   ├── common/          # Shared components
│   │   │   ├── SidebarNav.vue
│   │   │   └── TopBar.vue
│   │   └── dashboard/       # Dashboard widgets
│   │       ├── AIInsights.vue
│   │       ├── OccupancyChart.vue
│   │       ├── StatsCard.vue
│   │       └── TodayBookings.vue
│   ├── composables/         # Vue composables
│   │   ├── useApi.js
│   │   └── useNotification.js
│   ├── layouts/
│   │   └── DashboardLayout.vue
│   ├── router/
│   │   └── index.js         # Route definitions
│   ├── stores/              # Pinia stores
│   │   ├── auth.js
│   │   ├── bookings.js
│   │   ├── dashboard.js
│   │   ├── guests.js
│   │   ├── rooms.js
│   │   └── theme.js
│   ├── utils/
│   │   ├── api.js           # Axios instance
│   │   └── formatters.js    # Formatting helpers
│   ├── views/               # Page components
│   │   ├── BookingDetailView.vue
│   │   ├── BookingsView.vue
│   │   ├── ChatView.vue
│   │   ├── DashboardView.vue
│   │   ├── GuestDetailView.vue
│   │   ├── GuestsView.vue
│   │   ├── LoginView.vue
│   │   ├── NotFoundView.vue
│   │   ├── RoomsView.vue
│   │   └── SettingsView.vue
│   ├── App.vue
│   └── main.js
├── index.html
├── package.json
├── tailwind.config.js
├── vite.config.js
└── Dockerfile
```

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with your settings
```

### Development Server

```bash
npm run dev
# Server runs at http://localhost:3000
```

### Production Build

```bash
npm run build
# Output in dist/ folder
```

## Environment Variables

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Hotel Configuration
VITE_HOTEL_ID=1

# Theme Configuration
VITE_PRIMARY_COLOR=#2563eb
VITE_SECONDARY_COLOR=#64748b
VITE_ACCENT_COLOR=#f59e0b
VITE_FONT_FAMILY=Inter, system-ui, sans-serif
VITE_BORDER_RADIUS=8px

# Branding
VITE_BRAND_NAME=Hotel Management System
VITE_LOGO_URL=
VITE_FAVICON_URL=

# Feature Flags
VITE_ENABLE_WHATSAPP=true
VITE_ENABLE_AI_ASSISTANT=true
VITE_ENABLE_DARK_MODE=true

# Default Theme Mode (light/dark/system)
VITE_DEFAULT_THEME=system
```

## Theme System

### CSS Variables

The theme system uses CSS custom properties defined in `src/assets/styles/main.css`:

```css
:root {
  /* Colors */
  --color-primary: #2563eb;
  --color-secondary: #64748b;
  --color-accent: #f59e0b;

  /* Background */
  --color-background: #ffffff;
  --color-surface: #f8fafc;
  --color-card: #ffffff;

  /* Text */
  --color-text-primary: #1e293b;
  --color-text-secondary: #64748b;

  /* Typography */
  --font-family: 'Inter', sans-serif;
  --font-size-base: 16px;

  /* Spacing */
  --border-radius-sm: 4px;
  --border-radius-md: 8px;
  --border-radius-lg: 12px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
}

.dark {
  --color-background: #0f172a;
  --color-surface: #1e293b;
  --color-card: #334155;
  --color-text-primary: #f8fafc;
  --color-text-secondary: #94a3b8;
}
```

### Theme Store

Use the theme store to manage dark mode:

```javascript
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

// Toggle dark mode
themeStore.toggleDarkMode()

// Set specific mode
themeStore.setThemeMode('dark')  // 'light', 'dark', 'system'

// Load theme from backend
await themeStore.loadThemeSettings()
```

## Stores

### Auth Store
```javascript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Login
await authStore.login(email, password)

// Logout
authStore.logout()

// Check auth status
authStore.isAuthenticated
authStore.user
```

### Dashboard Store
```javascript
import { useDashboardStore } from '@/stores/dashboard'

const dashboardStore = useDashboardStore()

// Fetch all dashboard data
await dashboardStore.fetchAll()

// Access data
dashboardStore.stats
dashboardStore.todayCheckIns
dashboardStore.insights
```

### Rooms Store
```javascript
import { useRoomsStore } from '@/stores/rooms'

const roomsStore = useRoomsStore()

// Fetch rooms
await roomsStore.fetchRooms()

// Check availability
const available = await roomsStore.checkAvailability(checkIn, checkOut)

// Update status
await roomsStore.updateRoomStatus(roomId, 'maintenance')
```

### Bookings Store
```javascript
import { useBookingsStore } from '@/stores/bookings'

const bookingsStore = useBookingsStore()

// Fetch bookings
await bookingsStore.fetchBookings({ status: 'confirmed' })

// Create booking
await bookingsStore.createBooking(bookingData)

// Check-in/out
await bookingsStore.checkIn(bookingId, data)
await bookingsStore.checkOut(bookingId, data)
```

## Composables

### useApi
```javascript
import { useApi } from '@/composables/useApi'

const { isLoading, error, get, post, put, del } = useApi()

// Make API calls
const result = await get('/dashboard/stats?hotel_id=1')
if (result.success) {
  console.log(result.data)
}
```

### useNotification
```javascript
import { useNotification } from '@/composables/useNotification'

const notify = useNotification()

notify.success('Booking created successfully')
notify.error('Failed to save changes')
notify.warning('Low occupancy alert')
```

## Utility Functions

### Formatters
```javascript
import {
  formatCurrency,
  formatDate,
  formatPhone,
  getStatusClass
} from '@/utils/formatters'

formatCurrency(5000)        // '₹5,000'
formatDate('2024-01-15')    // '15 Jan 2024'
formatPhone('9876543210')   // '98765 43210'
getStatusClass('available') // 'badge-success'
```

## Components

### Button Classes
```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-outline">Outline</button>
<button class="btn btn-danger">Danger</button>
<button class="btn btn-sm">Small</button>
<button class="btn btn-lg">Large</button>
```

### Badge Classes
```html
<span class="badge badge-success">Available</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-error">Cancelled</span>
<span class="badge badge-info">Confirmed</span>
```

### Card Component
```html
<div class="card">
  <h2 class="text-lg font-semibold">Card Title</h2>
  <p class="text-secondary">Card content</p>
</div>
```

## Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Format code
npm run format
```

## License

MIT
