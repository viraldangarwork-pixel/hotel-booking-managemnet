<script setup>
import { ref, onMounted } from 'vue'
import { useBookingsStore } from '@/stores/bookings'
import { useRoomsStore } from '@/stores/rooms'
import { useGuestsStore } from '@/stores/guests'
import { useRouter } from 'vue-router'

const bookingsStore = useBookingsStore()
const roomsStore = useRoomsStore()
const guestsStore = useGuestsStore()
const router = useRouter()

const showAddModal = ref(false)
const isSubmitting = ref(false)
const formError = ref('')
const bookingForm = ref({
  guest_id: '',
  room_id: '',
  check_in_date: '',
  check_out_date: '',
  adults: 1,
  children: 0,
  extra_beds: 0,
  source: 'direct',
  special_requests: '',
})

onMounted(() => {
  bookingsStore.fetchBookings()
})

const getStatusBadge = (status) => {
  const badges = {
    pending: 'badge-warning',
    confirmed: 'badge-info',
    checked_in: 'badge-success',
    checked_out: 'badge-secondary',
    cancelled: 'badge-error',
    no_show: 'badge-error',
    inquiry: 'badge-secondary',
  }
  return badges[status] || 'badge-secondary'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

async function openAddModal() {
  bookingForm.value = {
    guest_id: '', room_id: '', check_in_date: '', check_out_date: '',
    adults: 1, children: 0, extra_beds: 0, source: 'direct', special_requests: '',
  }
  formError.value = ''
  // Load rooms and guests for the form dropdowns
  await Promise.all([
    roomsStore.fetchRooms(),
    guestsStore.fetchGuests(),
  ])
  showAddModal.value = true
}

function closeModal() {
  showAddModal.value = false
  formError.value = ''
}

async function handleAddBooking() {
  formError.value = ''
  if (!bookingForm.value.guest_id) { formError.value = 'Please select a guest'; return }
  if (!bookingForm.value.room_id) { formError.value = 'Please select a room'; return }
  if (!bookingForm.value.check_in_date) { formError.value = 'Check-in date is required'; return }
  if (!bookingForm.value.check_out_date) { formError.value = 'Check-out date is required'; return }

  if (bookingForm.value.check_out_date <= bookingForm.value.check_in_date) {
    formError.value = 'Check-out date must be after check-in date'
    return
  }

  isSubmitting.value = true
  const payload = {
    guest_id: Number(bookingForm.value.guest_id),
    room_id: Number(bookingForm.value.room_id),
    check_in_date: bookingForm.value.check_in_date,
    check_out_date: bookingForm.value.check_out_date,
    adults: Number(bookingForm.value.adults),
    children: Number(bookingForm.value.children),
    extra_beds: Number(bookingForm.value.extra_beds),
    source: bookingForm.value.source,
    special_requests: bookingForm.value.special_requests || null,
  }

  const result = await bookingsStore.createBooking(payload)
  isSubmitting.value = false

  if (result.success) {
    closeModal()
  } else {
    formError.value = result.error
  }
}

function viewBooking(bookingId) {
  router.push({ name: 'booking-detail', params: { id: bookingId } })
}

// Available rooms for the form (only show available rooms)
function getAvailableRooms() {
  return roomsStore.rooms.filter(r => r.status === 'available')
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Bookings</h1>
        <p class="text-secondary">Manage reservations and bookings</p>
      </div>
      <button class="btn btn-primary" @click="openAddModal">+ New Booking</button>
    </div>

    <!-- Loading state -->
    <div v-if="bookingsStore.isLoading" class="text-center py-12">
      <p class="text-secondary">Loading bookings...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="bookingsStore.bookings.length === 0" class="card text-center py-12">
      <p class="text-secondary mb-4">No bookings yet. Create your first booking to get started.</p>
      <button class="btn btn-primary" @click="openAddModal">+ New Booking</button>
    </div>

    <!-- Bookings table -->
    <div v-else class="card overflow-hidden !p-0">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-700" style="background-color: var(--color-surface)">
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
            <tr
              v-for="booking in bookingsStore.bookings"
              :key="booking.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer"
              @click="viewBooking(booking.id)"
            >
              <td class="px-4 py-3 font-medium text-primary-600">{{ booking.booking_ref }}</td>
              <td class="px-4 py-3">{{ booking.guest?.first_name }} {{ booking.guest?.last_name }}</td>
              <td class="px-4 py-3">{{ booking.room?.room_number || 'N/A' }}</td>
              <td class="px-4 py-3">{{ formatDate(booking.check_in_date) }}</td>
              <td class="px-4 py-3">{{ formatDate(booking.check_out_date) }}</td>
              <td class="px-4 py-3">
                <span :class="['badge', getStatusBadge(booking.status)]">
                  {{ booking.status?.replace('_', ' ') }}
                </span>
              </td>
              <td class="px-4 py-3">
                <button
                  class="text-primary-600 hover:underline text-sm"
                  @click.stop="viewBooking(booking.id)"
                >
                  View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- New Booking Modal -->
    <Teleport to="body">
      <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2 class="text-lg font-semibold">New Booking</h2>
            <button class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" @click="closeModal">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <form @submit.prevent="handleAddBooking">
            <div class="modal-body">
              <div v-if="formError" class="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-md text-sm">
                {{ formError }}
              </div>
              <div>
                <label class="label">Guest *</label>
                <select v-model="bookingForm.guest_id" class="select" required>
                  <option value="" disabled>Select guest</option>
                  <option v-for="g in guestsStore.guests" :key="g.id" :value="g.id">
                    {{ g.first_name }} {{ g.last_name }} - {{ g.phone }}
                  </option>
                </select>
              </div>
              <div>
                <label class="label">Room *</label>
                <select v-model="bookingForm.room_id" class="select" required>
                  <option value="" disabled>Select room</option>
                  <option v-for="r in getAvailableRooms()" :key="r.id" :value="r.id">
                    Room {{ r.room_number }} ({{ r.room_type?.name || 'N/A' }})
                  </option>
                </select>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="label">Check-in Date *</label>
                  <input v-model="bookingForm.check_in_date" type="date" class="input" required />
                </div>
                <div>
                  <label class="label">Check-out Date *</label>
                  <input v-model="bookingForm.check_out_date" type="date" class="input" required />
                </div>
              </div>
              <div class="grid grid-cols-3 gap-4">
                <div>
                  <label class="label">Adults</label>
                  <input v-model.number="bookingForm.adults" type="number" class="input" min="1" />
                </div>
                <div>
                  <label class="label">Children</label>
                  <input v-model.number="bookingForm.children" type="number" class="input" min="0" />
                </div>
                <div>
                  <label class="label">Extra Beds</label>
                  <input v-model.number="bookingForm.extra_beds" type="number" class="input" min="0" />
                </div>
              </div>
              <div>
                <label class="label">Booking Source</label>
                <select v-model="bookingForm.source" class="select">
                  <option value="direct">Direct</option>
                  <option value="website">Website</option>
                  <option value="whatsapp">WhatsApp</option>
                  <option value="phone">Phone</option>
                  <option value="walk_in">Walk-in</option>
                  <option value="ota">OTA</option>
                  <option value="corporate">Corporate</option>
                </select>
              </div>
              <div>
                <label class="label">Special Requests</label>
                <textarea v-model="bookingForm.special_requests" class="input" rows="2" placeholder="Any special requests..."></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
                {{ isSubmitting ? 'Creating...' : 'Create Booking' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>
