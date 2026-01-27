import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useDashboardStore = defineStore('dashboard', () => {
  const stats = ref(null)
  const todayCheckIns = ref([])
  const todayCheckOuts = ref([])
  const upcomingArrivals = ref([])
  const occupancyTrend = ref([])
  const revenueTrend = ref([])
  const insights = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const hotelId = import.meta.env.VITE_HOTEL_ID || 1

  async function fetchDashboardStats() {
    try {
      isLoading.value = true
      error.value = null

      const response = await api.get(`/dashboard/stats?hotel_id=${hotelId}`)
      stats.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load dashboard stats'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTodayBookings() {
    try {
      const response = await api.get(`/bookings/today?hotel_id=${hotelId}`)
      todayCheckIns.value = response.data.check_ins
      todayCheckOuts.value = response.data.check_outs
    } catch (err) {
      console.error('Failed to load today bookings:', err)
    }
  }

  async function fetchUpcomingArrivals(days = 7) {
    try {
      const response = await api.get(`/dashboard/upcoming-arrivals?hotel_id=${hotelId}&days=${days}`)
      upcomingArrivals.value = response.data
    } catch (err) {
      console.error('Failed to load upcoming arrivals:', err)
    }
  }

  async function fetchOccupancyTrend(days = 30) {
    try {
      const response = await api.get(`/dashboard/occupancy?hotel_id=${hotelId}&days=${days}`)
      occupancyTrend.value = response.data
    } catch (err) {
      console.error('Failed to load occupancy trend:', err)
    }
  }

  async function fetchRevenueTrend(days = 30) {
    try {
      const response = await api.get(`/dashboard/revenue?hotel_id=${hotelId}&days=${days}`)
      revenueTrend.value = response.data
    } catch (err) {
      console.error('Failed to load revenue trend:', err)
    }
  }

  async function fetchInsights() {
    try {
      const response = await api.get(`/dashboard/insights?hotel_id=${hotelId}`)
      insights.value = response.data
    } catch (err) {
      console.error('Failed to load insights:', err)
    }
  }

  async function fetchAll() {
    await Promise.all([
      fetchDashboardStats(),
      fetchTodayBookings(),
      fetchUpcomingArrivals(),
      fetchOccupancyTrend(14),
      fetchRevenueTrend(14),
      fetchInsights()
    ])
  }

  return {
    stats,
    todayCheckIns,
    todayCheckOuts,
    upcomingArrivals,
    occupancyTrend,
    revenueTrend,
    insights,
    isLoading,
    error,
    fetchDashboardStats,
    fetchTodayBookings,
    fetchUpcomingArrivals,
    fetchOccupancyTrend,
    fetchRevenueTrend,
    fetchInsights,
    fetchAll
  }
})
