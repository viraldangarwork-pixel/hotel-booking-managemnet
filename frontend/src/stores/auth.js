import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const refreshToken = ref(localStorage.getItem('refreshToken') || null)

  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || null)

  async function login(email, password) {
    try {
      const response = await api.post('/auth/login', { email, password })
      token.value = response.data.access_token
      refreshToken.value = response.data.refresh_token

      localStorage.setItem('token', token.value)
      localStorage.setItem('refreshToken', refreshToken.value)

      await fetchUser()
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      }
    }
  }

  async function fetchUser() {
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
    } catch (error) {
      logout()
    }
  }

  async function refreshAccessToken() {
    try {
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken.value
      })
      token.value = response.data.access_token
      refreshToken.value = response.data.refresh_token

      localStorage.setItem('token', token.value)
      localStorage.setItem('refreshToken', refreshToken.value)

      return true
    } catch (error) {
      logout()
      return false
    }
  }

  function logout() {
    user.value = null
    token.value = null
    refreshToken.value = null

    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  // Initialize: fetch user if token exists
  if (token.value) {
    fetchUser()
  }

  return {
    user,
    token,
    isAuthenticated,
    userRole,
    login,
    logout,
    fetchUser,
    refreshAccessToken
  }
})
