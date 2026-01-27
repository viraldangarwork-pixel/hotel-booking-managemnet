<script setup>
import { onMounted } from 'vue'
import { useBookingsStore } from '@/stores/bookings'

const bookingsStore = useBookingsStore()

onMounted(() => {
  bookingsStore.fetchBookings()
})

const getStatusBadge = (status) => {
  const badges = {
    pending: 'badge-warning',
    confirmed: 'badge-info',
    checked_in: 'badge-success',
    checked_out: 'badge-secondary',
    cancelled: 'badge-error'
  }
  return badges[status] || 'badge-secondary'
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Bookings</h1>
        <p class="text-secondary">Manage reservations and bookings</p>
      </div>
      <button class="btn btn-primary">New Booking</button>
    </div>

    <div class="card overflow-hidden">
      <table class="w-full">
        <thead class="bg-surface">
          <tr>
            <th class="px-4 py-3 text-left text-sm font-semibold">Booking Ref</th>
            <th class="px-4 py-3 text-left text-sm font-semibold">Guest</th>
            <th class="px-4 py-3 text-left text-sm font-semibold">Room</th>
            <th class="px-4 py-3 text-left text-sm font-semibold">Check-in</th>
            <th class="px-4 py-3 text-left text-sm font-semibold">Check-out</th>
            <th class="px-4 py-3 text-left text-sm font-semibold">Status</th>
            <th class="px-4 py-3 text-left text-sm font-semibold">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-for="booking in bookingsStore.bookings" :key="booking.id" class="hover:bg-surface">
            <td class="px-4 py-3 font-medium">{{ booking.booking_ref }}</td>
            <td class="px-4 py-3">{{ booking.guest?.first_name }} {{ booking.guest?.last_name }}</td>
            <td class="px-4 py-3">{{ booking.room?.room_number }}</td>
            <td class="px-4 py-3">{{ booking.check_in_date }}</td>
            <td class="px-4 py-3">{{ booking.check_out_date }}</td>
            <td class="px-4 py-3">
              <span :class="['badge', getStatusBadge(booking.status)]">{{ booking.status }}</span>
            </td>
            <td class="px-4 py-3">
              <button class="text-primary-600 hover:underline text-sm">View</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
