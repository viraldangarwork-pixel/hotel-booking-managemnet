import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useBookingsStore = defineStore('bookings', () => {
  const bookings = ref([])
  const currentBooking = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  const hotelId = import.meta.env.VITE_HOTEL_ID || 1

  async function fetchBookings(filters = {}) {
    try {
      isLoading.value = true
      error.value = null

      const params = new URLSearchParams({ hotel_id: hotelId, ...filters })
      const response = await api.get(`/bookings?${params}`)
      bookings.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load bookings'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchBooking(bookingId) {
    try {
      isLoading.value = true
      const response = await api.get(`/bookings/${bookingId}`)
      currentBooking.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load booking'
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function createBooking(bookingData) {
    try {
      const response = await api.post('/bookings', { ...bookingData, hotel_id: hotelId })
      bookings.value.unshift(response.data)
      return { success: true, data: response.data }
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Failed to create booking'
      }
    }
  }

  async function updateBooking(bookingId, bookingData) {
    try {
      const response = await api.put(`/bookings/${bookingId}`, bookingData)
      const index = bookings.value.findIndex(b => b.id === bookingId)
      if (index !== -1) {
        bookings.value[index] = response.data
      }
      if (currentBooking.value?.id === bookingId) {
        currentBooking.value = response.data
      }
      return { success: true, data: response.data }
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Failed to update booking'
      }
    }
  }

  async function checkIn(bookingId, data = {}) {
    try {
      const response = await api.post(`/bookings/${bookingId}/check-in`, data)
      const index = bookings.value.findIndex(b => b.id === bookingId)
      if (index !== -1) {
        bookings.value[index] = response.data
      }
      if (currentBooking.value?.id === bookingId) {
        currentBooking.value = response.data
      }
      return { success: true, data: response.data }
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Failed to check in'
      }
    }
  }

  async function checkOut(bookingId, data = {}) {
    try {
      const response = await api.post(`/bookings/${bookingId}/check-out`, data)
      const index = bookings.value.findIndex(b => b.id === bookingId)
      if (index !== -1) {
        bookings.value[index] = response.data
      }
      if (currentBooking.value?.id === bookingId) {
        currentBooking.value = response.data
      }
      return { success: true, data: response.data }
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Failed to check out'
      }
    }
  }

  async function cancelBooking(bookingId, reason = '') {
    try {
      const response = await api.post(`/bookings/${bookingId}/cancel?reason=${encodeURIComponent(reason)}`)
      const index = bookings.value.findIndex(b => b.id === bookingId)
      if (index !== -1) {
        bookings.value[index] = response.data
      }
      if (currentBooking.value?.id === bookingId) {
        currentBooking.value = response.data
      }
      return { success: true, data: response.data }
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Failed to cancel booking'
      }
    }
  }

  return {
    bookings,
    currentBooking,
    isLoading,
    error,
    fetchBookings,
    fetchBooking,
    createBooking,
    updateBooking,
    checkIn,
    checkOut,
    cancelBooking
  }
})
