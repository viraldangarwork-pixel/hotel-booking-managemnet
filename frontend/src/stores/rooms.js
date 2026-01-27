import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export const useRoomsStore = defineStore('rooms', () => {
  const rooms = ref([])
  const roomTypes = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const hotelId = import.meta.env.VITE_HOTEL_ID || 1

  // Computed properties
  const roomsByFloor = computed(() => {
    const grouped = {}
    rooms.value.forEach(room => {
      if (!grouped[room.floor]) {
        grouped[room.floor] = []
      }
      grouped[room.floor].push(room)
    })
    return grouped
  })

  const roomsByStatus = computed(() => {
    const counts = {
      available: 0,
      booked: 0,
      checked_in: 0,
      maintenance: 0,
      cleaning: 0
    }
    rooms.value.forEach(room => {
      if (counts[room.status] !== undefined) {
        counts[room.status]++
      }
    })
    return counts
  })

  // Actions
  async function fetchRooms(filters = {}) {
    try {
      isLoading.value = true
      error.value = null

      const params = new URLSearchParams({ hotel_id: hotelId, ...filters })
      const response = await api.get(`/rooms?${params}`)
      rooms.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load rooms'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchRoomTypes() {
    try {
      const response = await api.get(`/rooms/types?hotel_id=${hotelId}`)
      roomTypes.value = response.data
    } catch (err) {
      console.error('Failed to load room types:', err)
    }
  }

  async function checkAvailability(checkInDate, checkOutDate, roomTypeId = null) {
    try {
      const params = new URLSearchParams({
        hotel_id: hotelId,
        check_in_date: checkInDate,
        check_out_date: checkOutDate
      })
      if (roomTypeId) {
        params.append('room_type_id', roomTypeId)
      }

      const response = await api.get(`/rooms/availability?${params}`)
      return response.data
    } catch (err) {
      console.error('Failed to check availability:', err)
      return []
    }
  }

  async function updateRoomStatus(roomId, status) {
    try {
      const response = await api.put(`/rooms/${roomId}/status?status=${status}`)
      const index = rooms.value.findIndex(r => r.id === roomId)
      if (index !== -1) {
        rooms.value[index] = response.data
      }
      return { success: true }
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Failed to update room status'
      }
    }
  }

  async function createRoom(roomData) {
    try {
      const response = await api.post('/rooms', { ...roomData, hotel_id: hotelId })
      rooms.value.push(response.data)
      return { success: true, data: response.data }
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Failed to create room'
      }
    }
  }

  async function updateRoom(roomId, roomData) {
    try {
      const response = await api.put(`/rooms/${roomId}`, roomData)
      const index = rooms.value.findIndex(r => r.id === roomId)
      if (index !== -1) {
        rooms.value[index] = response.data
      }
      return { success: true, data: response.data }
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Failed to update room'
      }
    }
  }

  async function deleteRoom(roomId) {
    try {
      await api.delete(`/rooms/${roomId}`)
      rooms.value = rooms.value.filter(r => r.id !== roomId)
      return { success: true }
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Failed to delete room'
      }
    }
  }

  return {
    rooms,
    roomTypes,
    isLoading,
    error,
    roomsByFloor,
    roomsByStatus,
    fetchRooms,
    fetchRoomTypes,
    checkAvailability,
    updateRoomStatus,
    createRoom,
    updateRoom,
    deleteRoom
  }
})
