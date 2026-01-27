import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useGuestsStore = defineStore('guests', () => {
  const guests = ref([])
  const currentGuest = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  const hotelId = import.meta.env.VITE_HOTEL_ID || 1

  async function fetchGuests(filters = {}) {
    try {
      isLoading.value = true
      error.value = null

      const params = new URLSearchParams({ hotel_id: hotelId, ...filters })
      const response = await api.get(`/guests?${params}`)
      guests.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load guests'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchGuest(guestId) {
    try {
      isLoading.value = true
      const response = await api.get(`/guests/${guestId}`)
      currentGuest.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load guest'
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function searchGuests(query) {
    try {
      const response = await api.get(`/guests/search?hotel_id=${hotelId}&q=${encodeURIComponent(query)}`)
      return response.data
    } catch (err) {
      console.error('Failed to search guests:', err)
      return []
    }
  }

  async function createGuest(guestData) {
    try {
      const response = await api.post('/guests', { ...guestData, hotel_id: hotelId })
      guests.value.unshift(response.data)
      return { success: true, data: response.data }
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Failed to create guest'
      }
    }
  }

  async function findOrCreateGuest(guestData) {
    try {
      const response = await api.post('/guests/find-or-create', { ...guestData, hotel_id: hotelId })
      return { success: true, data: response.data }
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Failed to find/create guest'
      }
    }
  }

  async function updateGuest(guestId, guestData) {
    try {
      const response = await api.put(`/guests/${guestId}`, guestData)
      const index = guests.value.findIndex(g => g.id === guestId)
      if (index !== -1) {
        guests.value[index] = response.data
      }
      if (currentGuest.value?.id === guestId) {
        currentGuest.value = response.data
      }
      return { success: true, data: response.data }
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Failed to update guest'
      }
    }
  }

  async function toggleVIP(guestId, isVIP) {
    try {
      const response = await api.put(`/guests/${guestId}/vip?is_vip=${isVIP}`)
      const index = guests.value.findIndex(g => g.id === guestId)
      if (index !== -1) {
        guests.value[index] = response.data
      }
      return { success: true, data: response.data }
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Failed to update VIP status'
      }
    }
  }

  return {
    guests,
    currentGuest,
    isLoading,
    error,
    fetchGuests,
    fetchGuest,
    searchGuests,
    createGuest,
    findOrCreateGuest,
    updateGuest,
    toggleVIP
  }
})
