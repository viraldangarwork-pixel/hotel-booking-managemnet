<script setup>
import { ref, computed, onMounted } from 'vue'
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
const fieldErrors = ref({})
const successMessage = ref('')
const searchQuery = ref('')
const statusFilter = ref('')

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

const statusCounts = computed(() => {
  const counts = { pending: 0, confirmed: 0, checked_in: 0, checked_out: 0, cancelled: 0 }
  bookingsStore.bookings.forEach(b => {
    if (counts[b.status] !== undefined) counts[b.status]++
  })
  return counts
})

const filteredBookings = computed(() => {
  let list = bookingsStore.bookings
  if (statusFilter.value) {
    list = list.filter(b => b.status === statusFilter.value)
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(b =>
      (b.booking_ref || '').toLowerCase().includes(q) ||
      `${b.guest?.first_name || ''} ${b.guest?.last_name || ''}`.toLowerCase().includes(q) ||
      (b.room?.room_number || '').toString().includes(q)
    )
  }
  return list
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

const statusLabels = {
  pending: 'Pending',
  confirmed: 'Confirmed',
  checked_in: 'Checked In',
  checked_out: 'Checked Out',
  cancelled: 'Cancelled',
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function showSuccess(msg) {
  successMessage.value = msg
  setTimeout(() => { successMessage.value = '' }, 3000)
}

function validateForm() {
  fieldErrors.value = {}
  let valid = true

  if (!bookingForm.value.guest_id) {
    fieldErrors.value.guest_id = 'Please select a guest'
    valid = false
  }
  if (!bookingForm.value.room_id) {
    fieldErrors.value.room_id = 'Please select a room'
    valid = false
  }
  if (!bookingForm.value.check_in_date) {
    fieldErrors.value.check_in_date = 'Check-in date is required'
    valid = false
  }
  if (!bookingForm.value.check_out_date) {
    fieldErrors.value.check_out_date = 'Check-out date is required'
    valid = false
  }
  if (bookingForm.value.check_in_date && bookingForm.value.check_out_date) {
    if (bookingForm.value.check_out_date <= bookingForm.value.check_in_date) {
      fieldErrors.value.check_out_date = 'Check-out must be after check-in'
      valid = false
    }
  }
  if (bookingForm.value.adults < 1) {
    fieldErrors.value.adults = 'At least 1 adult required'
    valid = false
  }
  if (bookingForm.value.children < 0) {
    fieldErrors.value.children = 'Cannot be negative'
    valid = false
  }
  if (bookingForm.value.extra_beds < 0) {
    fieldErrors.value.extra_beds = 'Cannot be negative'
    valid = false
  }

  return valid
}

async function openAddModal() {
  bookingForm.value = {
    guest_id: '', room_id: '', check_in_date: '', check_out_date: '',
    adults: 1, children: 0, extra_beds: 0, source: 'direct', special_requests: '',
  }
  formError.value = ''
  fieldErrors.value = {}
  await Promise.all([
    roomsStore.fetchRooms(),
    guestsStore.fetchGuests(),
  ])
  showAddModal.value = true
}

function closeModal() {
  showAddModal.value = false
  formError.value = ''
  fieldErrors.value = {}
}

async function handleAddBooking() {
  formError.value = ''
  if (!validateForm()) return

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
    showSuccess('Booking created successfully!')
  } else {
    formError.value = result.error
  }
}

function viewBooking(bookingId) {
  router.push({ name: 'booking-detail', params: { id: bookingId } })
}

function getAvailableRooms() {
  return roomsStore.rooms.filter(r => r.status === 'available')
}

function toggleStatusFilter(status) {
  statusFilter.value = statusFilter.value === status ? '' : status
}

function getTodayDate() {
  return new Date().toISOString().split('T')[0]
}
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Bookings</h1>
        <p class="text-secondary">Manage reservations and bookings</p>
      </div>
      <button class="btn btn-primary" @click="openAddModal">+ New Booking</button>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="alert alert-success animate-slide-down">
      {{ successMessage }}
    </div>

    <!-- Status Summary Cards -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
      <div
        v-for="(label, key) in statusLabels"
        :key="key"
        @click="toggleStatusFilter(key)"
        :class="[
          'card !p-3 text-center cursor-pointer transition-all',
          statusFilter === key ? 'ring-2 ring-primary-500 shadow-lg' : 'hover:shadow-md'
        ]"
      >
        <div class="text-2xl font-bold">{{ statusCounts[key] || 0 }}</div>
        <div class="text-xs text-secondary mt-1">{{ label }}</div>
      </div>
    </div>

    <!-- Search -->
    <div class="flex items-center gap-3">
      <div class="relative flex-1 max-w-md">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="input !pl-10"
          placeholder="Search by ref, guest name, room..."
        />
      </div>
      <span v-if="statusFilter" class="text-sm text-secondary">
        Filtered: <span class="font-medium text-primary-600">{{ statusLabels[statusFilter] }}</span>
        <button @click="statusFilter = ''" class="ml-1 text-red-500 hover:text-red-700">&times;</button>
      </span>
    </div>

    <!-- Loading state -->
    <div v-if="bookingsStore.isLoading" class="text-center py-12">
      <div class="spinner mx-auto mb-3"></div>
      <p class="text-secondary">Loading bookings...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="filteredBookings.length === 0" class="card text-center py-12">
      <svg class="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <p class="text-secondary mb-4" v-if="searchQuery || statusFilter">No bookings match your search.</p>
      <p class="text-secondary mb-4" v-else>No bookings yet. Create your first booking to get started.</p>
      <button v-if="!searchQuery && !statusFilter" class="btn btn-primary" @click="openAddModal">+ New Booking</button>
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
              <th class="px-4 py-3 text-left text-sm font-semibold">Actual Check-in</th>
              <th class="px-4 py-3 text-left text-sm font-semibold">Status</th>
              <th class="px-4 py-3 text-left text-sm font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="(booking, idx) in filteredBookings"
              :key="booking.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer stagger-item"
              @click="viewBooking(booking.id)"
            >
              <td class="px-4 py-3 font-medium text-primary-600">{{ booking.booking_ref }}</td>
              <td class="px-4 py-3">{{ booking.guest?.first_name }} {{ booking.guest?.last_name }}</td>
              <td class="px-4 py-3">{{ booking.room?.room_number || 'N/A' }}</td>
              <td class="px-4 py-3">{{ formatDate(booking.check_in_date) }}</td>
              <td class="px-4 py-3">{{ formatDate(booking.check_out_date) }}</td>
              <td class="px-4 py-3">
                <span v-if="booking.actual_check_in" class="text-green-600 text-sm">
                  {{ formatDateTime(booking.actual_check_in) }}
                </span>
                <span v-else class="text-gray-400 text-sm">—</span>
              </td>
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
        <div class="modal-content modal-content-wide">
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
              <div v-if="formError" class="alert alert-error">
                {{ formError }}
              </div>

              <!-- Guest -->
              <div>
                <label class="label">Guest *</label>
                <select v-model="bookingForm.guest_id" :class="['select', fieldErrors.guest_id ? 'border-red-500' : '']">
                  <option value="" disabled>Select guest</option>
                  <option v-for="g in guestsStore.guests" :key="g.id" :value="g.id">
                    {{ g.first_name }} {{ g.last_name }} - {{ g.phone }}
                  </option>
                </select>
                <p v-if="fieldErrors.guest_id" class="text-red-500 text-xs mt-1">{{ fieldErrors.guest_id }}</p>
              </div>

              <!-- Room -->
              <div>
                <label class="label">Room *</label>
                <select v-model="bookingForm.room_id" :class="['select', fieldErrors.room_id ? 'border-red-500' : '']">
                  <option value="" disabled>Select room</option>
                  <option v-for="r in getAvailableRooms()" :key="r.id" :value="r.id">
                    Room {{ r.room_number }} ({{ r.room_type?.name || 'N/A' }})
                  </option>
                </select>
                <p v-if="fieldErrors.room_id" class="text-red-500 text-xs mt-1">{{ fieldErrors.room_id }}</p>
                <p v-if="getAvailableRooms().length === 0" class="text-orange-500 text-xs mt-1">No rooms available currently</p>
              </div>

              <!-- Dates -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="label">Check-in Date *</label>
                  <input
                    v-model="bookingForm.check_in_date"
                    type="date"
                    :min="getTodayDate()"
                    :class="['input', fieldErrors.check_in_date ? 'border-red-500' : '']"
                  />
                  <p v-if="fieldErrors.check_in_date" class="text-red-500 text-xs mt-1">{{ fieldErrors.check_in_date }}</p>
                </div>
                <div>
                  <label class="label">Check-out Date *</label>
                  <input
                    v-model="bookingForm.check_out_date"
                    type="date"
                    :min="bookingForm.check_in_date || getTodayDate()"
                    :class="['input', fieldErrors.check_out_date ? 'border-red-500' : '']"
                  />
                  <p v-if="fieldErrors.check_out_date" class="text-red-500 text-xs mt-1">{{ fieldErrors.check_out_date }}</p>
                </div>
              </div>

              <!-- Occupancy -->
              <div class="grid grid-cols-3 gap-4">
                <div>
                  <label class="label">Adults *</label>
                  <input
                    v-model.number="bookingForm.adults"
                    type="number"
                    min="1"
                    max="10"
                    :class="['input', fieldErrors.adults ? 'border-red-500' : '']"
                  />
                  <p v-if="fieldErrors.adults" class="text-red-500 text-xs mt-1">{{ fieldErrors.adults }}</p>
                </div>
                <div>
                  <label class="label">Children</label>
                  <input
                    v-model.number="bookingForm.children"
                    type="number"
                    min="0"
                    max="10"
                    :class="['input', fieldErrors.children ? 'border-red-500' : '']"
                  />
                  <p v-if="fieldErrors.children" class="text-red-500 text-xs mt-1">{{ fieldErrors.children }}</p>
                </div>
                <div>
                  <label class="label">Extra Beds</label>
                  <input
                    v-model.number="bookingForm.extra_beds"
                    type="number"
                    min="0"
                    max="5"
                    :class="['input', fieldErrors.extra_beds ? 'border-red-500' : '']"
                  />
                  <p v-if="fieldErrors.extra_beds" class="text-red-500 text-xs mt-1">{{ fieldErrors.extra_beds }}</p>
                </div>
              </div>

              <!-- Source -->
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

              <!-- Special Requests -->
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
