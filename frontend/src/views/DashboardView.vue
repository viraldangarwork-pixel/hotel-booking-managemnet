<script setup>
import { onMounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import StatsCard from '@/components/dashboard/StatsCard.vue'
import OccupancyChart from '@/components/dashboard/OccupancyChart.vue'
import TodayBookings from '@/components/dashboard/TodayBookings.vue'
import AIInsights from '@/components/dashboard/AIInsights.vue'

const dashboardStore = useDashboardStore()

onMounted(() => {
  dashboardStore.fetchAll()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Dashboard</h1>
        <p class="text-secondary">Welcome back! Here's what's happening today.</p>
      </div>
      <button @click="dashboardStore.fetchAll()" class="btn btn-secondary">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatsCard
        title="Total Rooms"
        :value="dashboardStore.stats?.total_rooms || 0"
        icon="rooms"
        color="blue"
      />
      <StatsCard
        title="Occupancy Rate"
        :value="`${dashboardStore.stats?.occupancy_rate || 0}%`"
        icon="chart"
        color="green"
      />
      <StatsCard
        title="Today's Check-ins"
        :value="dashboardStore.stats?.today_check_ins || 0"
        icon="checkin"
        color="yellow"
      />
      <StatsCard
        title="Today's Revenue"
        :value="`₹${dashboardStore.stats?.revenue_today || 0}`"
        icon="revenue"
        color="purple"
      />
    </div>

    <!-- Room status overview -->
    <div class="card">
      <h2 class="text-lg font-semibold mb-4">Room Status</h2>
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div class="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div class="text-2xl font-bold text-green-600">{{ dashboardStore.stats?.rooms_status?.available || 0 }}</div>
          <div class="text-sm text-green-700 dark:text-green-400">Available</div>
        </div>
        <div class="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div class="text-2xl font-bold text-blue-600">{{ dashboardStore.stats?.rooms_status?.booked || 0 }}</div>
          <div class="text-sm text-blue-700 dark:text-blue-400">Booked</div>
        </div>
        <div class="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
          <div class="text-2xl font-bold text-yellow-600">{{ dashboardStore.stats?.rooms_status?.checked_in || 0 }}</div>
          <div class="text-sm text-yellow-700 dark:text-yellow-400">Occupied</div>
        </div>
        <div class="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
          <div class="text-2xl font-bold text-orange-600">{{ dashboardStore.stats?.rooms_status?.cleaning || 0 }}</div>
          <div class="text-sm text-orange-700 dark:text-orange-400">Cleaning</div>
        </div>
        <div class="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
          <div class="text-2xl font-bold text-red-600">{{ dashboardStore.stats?.rooms_status?.maintenance || 0 }}</div>
          <div class="text-sm text-red-700 dark:text-red-400">Maintenance</div>
        </div>
      </div>
    </div>

    <!-- Main content grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Today's bookings -->
      <div class="lg:col-span-2">
        <TodayBookings
          :check-ins="dashboardStore.todayCheckIns"
          :check-outs="dashboardStore.todayCheckOuts"
        />
      </div>

      <!-- AI Insights -->
      <div>
        <AIInsights :insights="dashboardStore.insights" />
      </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <OccupancyChart :data="dashboardStore.occupancyTrend" title="Occupancy Trend" />
      <OccupancyChart :data="dashboardStore.revenueTrend" title="Revenue Trend" type="revenue" />
    </div>
  </div>
</template>
