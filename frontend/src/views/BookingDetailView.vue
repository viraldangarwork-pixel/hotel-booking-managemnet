<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useBookingsStore } from '@/stores/bookings'

const route = useRoute()
const bookingsStore = useBookingsStore()

onMounted(() => {
  bookingsStore.fetchBooking(route.params.id)
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">Booking Details</h1>
    <div class="card" v-if="bookingsStore.currentBooking">
      <p>Booking Ref: {{ bookingsStore.currentBooking.booking_ref }}</p>
    </div>
  </div>
</template>
