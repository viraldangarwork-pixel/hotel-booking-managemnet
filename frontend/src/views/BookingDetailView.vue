<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBookingsStore } from '@/stores/bookings'

const route = useRoute()
const router = useRouter()
const bookingsStore = useBookingsStore()

const actionLoading = ref('')
const actionError = ref('')
const actionSuccess = ref('')
const showCancelModal = ref(false)
const cancelReason = ref('')

const booking = computed(() => bookingsStore.currentBooking)

onMounted(async () => {
  await bookingsStore.fetchBooking(route.params.id)
})

function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatDateTime(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function getStatusBadge(status) {
  const map = { pending: 'badge-warning', confirmed: 'badge-info', checked_in: 'badge-success', checked_out: 'badge-secondary', cancelled: 'badge-error', no_show: 'badge-error', inquiry: 'badge-secondary' }
  return map[status] || 'badge-secondary'
}

function getNights() {
  if (!booking.value) return 0
  const ci = new Date(booking.value.check_in_date)
  const co = new Date(booking.value.check_out_date)
  return Math.ceil((co - ci) / (1000 * 60 * 60 * 24))
}

async function handleCheckIn() {
  actionLoading.value = 'checkin'
  actionError.value = ''
  const result = await bookingsStore.checkIn(booking.value.id, {})
  actionLoading.value = ''
  if (result.success) {
    actionSuccess.value = 'Guest checked in successfully'
    setTimeout(() => { actionSuccess.value = '' }, 3000)
  } else {
    actionError.value = result.error
  }
}

async function handleCheckOut() {
  actionLoading.value = 'checkout'
  actionError.value = ''
  const result = await bookingsStore.checkOut(booking.value.id, {})
  actionLoading.value = ''
  if (result.success) {
    actionSuccess.value = 'Guest checked out successfully'
    setTimeout(() => { actionSuccess.value = '' }, 3000)
  } else {
    actionError.value = result.error
  }
}

async function handleCancel() {
  actionLoading.value = 'cancel'
  actionError.value = ''
  const result = await bookingsStore.cancelBooking(booking.value.id, cancelReason.value)
  actionLoading.value = ''
  showCancelModal.value = false
  if (result.success) {
    actionSuccess.value = 'Booking cancelled'
    setTimeout(() => { actionSuccess.value = '' }, 3000)
  } else {
    actionError.value = result.error
  }
}
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <button @click="router.push({ name: 'bookings' })" class="btn btn-secondary btn-sm">
      <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      Back to Bookings
    </button>

    <div v-if="bookingsStore.isLoading && !booking" class="flex justify-center py-12">
      <div class="spinner"></div>
    </div>

    <template v-if="booking">
      <!-- Alerts -->
      <div v-if="actionError" class="alert alert-error">{{ actionError }}</div>
      <div v-if="actionSuccess" class="alert alert-success">{{ actionSuccess }}</div>

      <!-- Header -->
      <div class="card animate-slide-down">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-2xl font-bold">{{ booking.booking_ref }}</h1>
              <span :class="['badge', getStatusBadge(booking.status)]">{{ booking.status?.replace('_', ' ') }}</span>
            </div>
            <p class="text-secondary mt-1">Created {{ formatDateTime(booking.created_at) }}</p>
          </div>
          <div class="flex items-center gap-2 flex-wrap">
            <button
              v-if="booking.status === 'confirmed' || booking.status === 'pending'"
              @click="handleCheckIn"
              :disabled="actionLoading === 'checkin'"
              class="btn btn-success btn-sm"
            >{{ actionLoading === 'checkin' ? 'Processing...' : 'Check In' }}</button>
            <button
              v-if="booking.status === 'checked_in'"
              @click="handleCheckOut"
              :disabled="actionLoading === 'checkout'"
              class="btn btn-primary btn-sm"
            >{{ actionLoading === 'checkout' ? 'Processing...' : 'Check Out' }}</button>
            <button
              v-if="!['checked_out', 'cancelled'].includes(booking.status)"
              @click="showCancelModal = true"
              class="btn btn-danger btn-sm"
            >Cancel</button>
          </div>
        </div>
      </div>

      <!-- Details grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Booking info -->
        <div class="lg:col-span-2 space-y-6">
          <div class="card animate-slide-up">
            <h2 class="text-lg font-semibold mb-4">Booking Details</h2>
            <div class="grid grid-cols-2 gap-y-4 gap-x-8">
              <div><span class="label">Check-in Date</span><p class="font-medium">{{ formatDate(booking.check_in_date) }}</p></div>
              <div><span class="label">Check-out Date</span><p class="font-medium">{{ formatDate(booking.check_out_date) }}</p></div>
              <div><span class="label">Nights</span><p class="font-medium">{{ getNights() }}</p></div>
              <div><span class="label">Source</span><p class="font-medium capitalize">{{ booking.source?.replace('_', ' ') }}</p></div>
              <div><span class="label">Adults</span><p class="font-medium">{{ booking.adults }}</p></div>
              <div><span class="label">Children</span><p class="font-medium">{{ booking.children }}</p></div>
              <div><span class="label">Extra Beds</span><p class="font-medium">{{ booking.extra_beds }}</p></div>
              <div><span class="label">Room</span><p class="font-medium">{{ booking.room?.room_number || 'N/A' }} ({{ booking.room?.room_type?.name || '' }})</p></div>
            </div>

            <!-- Actual check-in/out times -->
            <div v-if="booking.actual_check_in || booking.actual_check_out" class="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
              <h3 class="font-medium mb-3">Actual Times</h3>
              <div class="grid grid-cols-2 gap-4">
                <div v-if="booking.actual_check_in">
                  <span class="label">Actual Check-in</span>
                  <p class="font-medium text-green-600">{{ formatDateTime(booking.actual_check_in) }}</p>
                </div>
                <div v-if="booking.actual_check_out">
                  <span class="label">Actual Check-out</span>
                  <p class="font-medium text-purple-600">{{ formatDateTime(booking.actual_check_out) }}</p>
                </div>
              </div>
            </div>

            <div v-if="booking.special_requests" class="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
              <span class="label">Special Requests</span>
              <p class="mt-1">{{ booking.special_requests }}</p>
            </div>
          </div>

          <!-- Guest info -->
          <div class="card animate-slide-up" v-if="booking.guest">
            <h2 class="text-lg font-semibold mb-4">Guest Information</h2>
            <div class="flex items-center space-x-4">
              <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
                <span class="text-primary-600 dark:text-primary-400 font-semibold">
                  {{ booking.guest.first_name?.charAt(0) }}{{ booking.guest.last_name?.charAt(0) }}
                </span>
              </div>
              <div>
                <p class="font-semibold">{{ booking.guest.first_name }} {{ booking.guest.last_name }}</p>
                <p class="text-sm text-secondary">{{ booking.guest.phone }} {{ booking.guest.email ? '| ' + booking.guest.email : '' }}</p>
              </div>
              <button @click="router.push({ name: 'guest-detail', params: { id: booking.guest_id } })" class="btn btn-outline btn-sm ml-auto">View Profile</button>
            </div>
          </div>
        </div>

        <!-- Pricing sidebar -->
        <div class="space-y-6">
          <div class="card animate-slide-in-right">
            <h2 class="text-lg font-semibold mb-4">Pricing</h2>
            <div class="space-y-3">
              <div class="flex justify-between"><span class="text-secondary">Room Rate / Night</span><span class="font-medium">{{ booking.room_rate }}</span></div>
              <div class="flex justify-between"><span class="text-secondary">Nights</span><span class="font-medium">{{ getNights() }}</span></div>
              <div v-if="Number(booking.extra_bed_charge) > 0" class="flex justify-between"><span class="text-secondary">Extra Bed Charge</span><span class="font-medium">{{ booking.extra_bed_charge }}</span></div>
              <div class="border-t border-gray-200 dark:border-gray-700 pt-3 flex justify-between"><span class="text-secondary">Subtotal</span><span class="font-medium">{{ booking.subtotal }}</span></div>
              <div v-if="Number(booking.discount_amount) > 0" class="flex justify-between text-green-600"><span>Discount</span><span>-{{ booking.discount_amount }}</span></div>
              <div class="flex justify-between"><span class="text-secondary">Tax</span><span class="font-medium">{{ booking.tax_amount }}</span></div>
              <div class="border-t border-gray-200 dark:border-gray-700 pt-3 flex justify-between text-lg font-bold"><span>Total</span><span>{{ booking.total_amount }}</span></div>
              <div class="flex justify-between"><span class="text-secondary">Paid</span><span class="font-medium text-green-600">{{ booking.amount_paid }}</span></div>
              <div v-if="!booking.is_paid" class="flex justify-between text-red-600"><span class="font-medium">Balance Due</span><span class="font-bold">{{ (Number(booking.total_amount) - Number(booking.amount_paid)).toFixed(2) }}</span></div>
              <span v-else class="badge badge-success">Fully Paid</span>
            </div>
          </div>

          <div v-if="booking.cancelled_at" class="card animate-slide-in-right border-2 border-red-300 dark:border-red-700">
            <h2 class="text-lg font-semibold text-red-600 mb-2">Cancelled</h2>
            <p class="text-sm text-secondary">{{ formatDateTime(booking.cancelled_at) }}</p>
            <p v-if="booking.cancellation_reason" class="mt-2 text-sm">{{ booking.cancellation_reason }}</p>
          </div>
        </div>
      </div>
    </template>

    <!-- Cancel Modal -->
    <Teleport to="body">
      <div v-if="showCancelModal" class="modal-overlay" @click.self="showCancelModal = false">
        <div class="modal-content" style="max-width: 400px">
          <div class="modal-header">
            <h2 class="text-lg font-semibold text-red-600">Cancel Booking</h2>
            <button @click="showCancelModal = false" class="text-gray-400 hover:text-gray-600">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <p class="text-sm text-secondary mb-4">Are you sure you want to cancel this booking? This action cannot be undone.</p>
            <label class="label">Cancellation Reason</label>
            <textarea v-model="cancelReason" class="input" rows="3" placeholder="Enter reason for cancellation..."></textarea>
          </div>
          <div class="modal-footer">
            <button @click="showCancelModal = false" class="btn btn-secondary">Keep Booking</button>
            <button @click="handleCancel" :disabled="actionLoading === 'cancel'" class="btn btn-danger">
              {{ actionLoading === 'cancel' ? 'Cancelling...' : 'Cancel Booking' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
