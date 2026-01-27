import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue')
      },
      {
        path: 'rooms',
        name: 'rooms',
        component: () => import('@/views/RoomsView.vue')
      },
      {
        path: 'bookings',
        name: 'bookings',
        component: () => import('@/views/BookingsView.vue')
      },
      {
        path: 'bookings/:id',
        name: 'booking-detail',
        component: () => import('@/views/BookingDetailView.vue')
      },
      {
        path: 'guests',
        name: 'guests',
        component: () => import('@/views/GuestsView.vue')
      },
      {
        path: 'guests/:id',
        name: 'guest-detail',
        component: () => import('@/views/GuestDetailView.vue')
      },
      {
        path: 'chat',
        name: 'chat',
        component: () => import('@/views/ChatView.vue')
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/views/SettingsView.vue')
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
