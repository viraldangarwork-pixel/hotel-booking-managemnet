<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoomsStore } from '@/stores/rooms'
import { useBookingsStore } from '@/stores/bookings'

const roomsStore = useRoomsStore()
const bookingsStore = useBookingsStore()

const showAddModal = ref(false)
const isSubmitting = ref(false)
const formError = ref('')
const successMsg = ref('')
const filterStatus = ref('')

const roomForm = ref({
  room_number: '',
  floor: 1,
  room_type_id: '',
  custom_price: '',
  notes: '',
})
const fieldErrors = ref({})

onMounted(async () => {
  await roomsStore.fetchRooms()
  await roomsStore.fetchRoomTypes()
  await bookingsStore.fetchBookings()
})

const getStatusColor = (status) => {
  const colors = {
    available: 'bg-green-500',
    booked: 'bg-blue-500',
    checked_in: 'bg-yellow-500',
    maintenance: 'bg-red-500',
    cleaning: 'bg-orange-500',
    checked_out: 'bg-purple-500'
  }
  return colors[status] || 'bg-gray-500'
}

const getStatusBorder = (status) => {
  const borders = {
    available: 'border-green-500 bg-green-50 dark:bg-green-900/20',
    booked: 'border-blue-500 bg-blue-50 dark:bg-blue-900/20',
    checked_in: 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20',
    maintenance: 'border-red-500 bg-red-50 dark:bg-red-900/20',
    cleaning: 'border-orange-500 bg-orange-50 dark:bg-orange-900/20',
    checked_out: 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
  }
  return borders[status] || ''
}

// Get booking info for a room (if booked or checked in)
function getRoomBooking(room) {
  if (!['booked', 'checked_in'].includes(room.status)) return null
  return bookingsStore.bookings.find(b =>
    b.room_id === room.id &&
    ['confirmed', 'checked_in', 'pending'].includes(b.status)
  )
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function validateRoomForm() {
  fieldErrors.value = {}
  if (!roomForm.value.room_number.trim()) fieldErrors.value.room_number = 'Room number is required'
  if (!roomForm.value.room_type_id) fieldErrors.value.room_type_id = 'Room type is required'
  if (roomForm.value.floor < 1) fieldErrors.value.floor = 'Floor must be at least 1'
  if (roomForm.value.custom_price && Number(roomForm.value.custom_price) < 0) fieldErrors.value.custom_price = 'Price cannot be negative'
  return Object.keys(fieldErrors.value).length === 0
}

function openAddModal() {
  roomForm.value = { room_number: '', floor: 1, room_type_id: '', custom_price: '', notes: '' }
  formError.value = ''
  fieldErrors.value = {}
  showAddModal.value = true
}

function closeModal() {
  showAddModal.value = false
  formError.value = ''
  fieldErrors.value = {}
}

async function handleAddRoom() {
  formError.value = ''
  if (!validateRoomForm()) {
    formError.value = 'Please fix the errors below'
    return
  }

  isSubmitting.value = true
  const payload = {
    room_number: roomForm.value.room_number.trim(),
    floor: Number(roomForm.value.floor),
    room_type_id: Number(roomForm.value.room_type_id),
    notes: roomForm.value.notes || null,
  }
  if (roomForm.value.custom_price) {
    payload.custom_price = Number(roomForm.value.custom_price)
  }

  const result = await roomsStore.createRoom(payload)
  isSubmitting.value = false

  if (result.success) {
    closeModal()
    successMsg.value = `Room ${result.data.room_number} added successfully`
    setTimeout(() => { successMsg.value = '' }, 3000)
  } else {
    formError.value = result.error
  }
}

async function handleStatusChange(roomId, newStatus) {
  await roomsStore.updateRoomStatus(roomId, newStatus)
}

const filteredRoomsByFloor = computed(() => {
  let rooms = roomsStore.rooms
  if (filterStatus.value) {
    rooms = rooms.filter(r => r.status === filterStatus.value)
  }
  const grouped = {}
  rooms.forEach(room => {
    if (!grouped[room.floor]) grouped[room.floor] = []
    grouped[room.floor].push(room)
  })
  return grouped
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Rooms</h1>
        <p class="text-secondary">Manage hotel rooms and availability</p>
      </div>
      <button class="btn btn-primary" @click="openAddModal">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        Add Room
      </button>
    </div>

    <!-- Success message -->
    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>

    <!-- Room status summary -->
    <div class="grid grid-cols-2 md:grid-cols-6 gap-4 animate-slide-down">
      <div v-for="(count, status) in roomsStore.roomsByStatus" :key="status"
        class="card card-hover text-center cursor-pointer"
        :class="filterStatus === status ? 'ring-2 ring-primary-500' : ''"
        @click="filterStatus = filterStatus === status ? '' : status"
      >
        <div class="flex items-center justify-center space-x-2">
          <span :class="['w-3 h-3 rounded-full', getStatusColor(status)]"></span>
          <span class="capitalize text-sm">{{ status.replace('_', ' ') }}</span>
        </div>
        <p class="text-2xl font-bold mt-2">{{ count }}</p>
      </div>
    </div>

    <!-- Filter indicator -->
    <div v-if="filterStatus" class="flex items-center gap-2">
      <span class="text-sm text-secondary">Filtered by:</span>
      <span class="badge badge-info capitalize">{{ filterStatus.replace('_', ' ') }}</span>
      <button @click="filterStatus = ''" class="text-xs text-primary-600 hover:underline">Clear filter</button>
    </div>

    <!-- Loading state -->
    <div v-if="roomsStore.isLoading" class="flex justify-center py-12">
      <div class="spinner"></div>
    </div>

    <!-- Empty state -->
    <div v-else-if="roomsStore.rooms.length === 0" class="card text-center py-12 animate-slide-up">
      <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
      <p class="text-secondary mb-4">No rooms found. Add your first room to get started.</p>
      <button class="btn btn-primary" @click="openAddModal">+ Add Room</button>
    </div>

    <!-- Rooms grid by floor -->
    <div v-else v-for="(rooms, floor) in filteredRoomsByFloor" :key="floor" class="card animate-slide-up">
      <h3 class="text-lg font-semibold mb-4">Floor {{ floor }}</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div
          v-for="room in rooms"
          :key="room.id"
          class="p-4 rounded-lg border-2 cursor-pointer hover:shadow-md transition-all relative group stagger-item"
          :class="getStatusBorder(room.status)"
        >
          <p class="font-bold text-lg">{{ room.room_number }}</p>
          <p class="text-sm text-secondary">{{ room.room_type?.name || 'N/A' }}</p>
          <span class="text-xs capitalize" :class="getStatusColor(room.status).replace('bg-', 'text-')">
            {{ room.status.replace('_', ' ') }}
          </span>

          <!-- Booking info for booked/checked_in rooms -->
          <div v-if="getRoomBooking(room)" class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
            <p class="text-xs font-medium text-gray-700 dark:text-gray-300">
              {{ getRoomBooking(room).guest?.first_name }} {{ getRoomBooking(room).guest?.last_name }}
            </p>
            <div class="text-xs text-secondary mt-0.5 space-y-0.5">
              <p>In: {{ formatDate(getRoomBooking(room).check_in_date) }}</p>
              <p>Out: {{ formatDate(getRoomBooking(room).check_out_date) }}</p>
              <p v-if="getRoomBooking(room).actual_check_in" class="text-green-600 dark:text-green-400">
                Checked in: {{ formatDateTime(getRoomBooking(room).actual_check_in) }}
              </p>
              <p v-if="getRoomBooking(room).actual_check_out" class="text-purple-600 dark:text-purple-400">
                Checked out: {{ formatDateTime(getRoomBooking(room).actual_check_out) }}
              </p>
            </div>
          </div>

          <!-- Quick status change -->
          <div class="hidden group-hover:block absolute top-1 right-1">
            <select
              class="text-xs rounded border border-gray-300 dark:border-gray-600 dark:bg-gray-700 p-0.5"
              :value="room.status"
              @change="handleStatusChange(room.id, $event.target.value)"
              @click.stop
            >
              <option value="available">Available</option>
              <option value="booked">Booked</option>
              <option value="checked_in">Checked In</option>
              <option value="maintenance">Maintenance</option>
              <option value="cleaning">Cleaning</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Room Modal -->
    <Teleport to="body">
      <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2 class="text-lg font-semibold">Add New Room</h2>
            <button class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" @click="closeModal">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <form @submit.prevent="handleAddRoom">
            <div class="modal-body">
              <div v-if="formError" class="alert alert-error">{{ formError }}</div>
              <div>
                <label class="label">Room Number *</label>
                <input v-model="roomForm.room_number" type="text" :class="['input', fieldErrors.room_number ? 'input-error' : '']" placeholder="e.g. 101" />
                <p v-if="fieldErrors.room_number" class="text-xs text-red-500 mt-1">{{ fieldErrors.room_number }}</p>
              </div>
              <div>
                <label class="label">Floor *</label>
                <input v-model.number="roomForm.floor" type="number" :class="['input', fieldErrors.floor ? 'input-error' : '']" min="1" />
                <p v-if="fieldErrors.floor" class="text-xs text-red-500 mt-1">{{ fieldErrors.floor }}</p>
              </div>
              <div>
                <label class="label">Room Type *</label>
                <select v-model="roomForm.room_type_id" :class="['select', fieldErrors.room_type_id ? 'input-error' : '']">
                  <option value="" disabled>Select room type</option>
                  <option v-for="rt in roomsStore.roomTypes" :key="rt.id" :value="rt.id">
                    {{ rt.name }} - ${{ rt.base_price }}/night
                  </option>
                </select>
                <p v-if="fieldErrors.room_type_id" class="text-xs text-red-500 mt-1">{{ fieldErrors.room_type_id }}</p>
              </div>
              <div>
                <label class="label">Custom Price (optional)</label>
                <input v-model="roomForm.custom_price" type="number" :class="['input', fieldErrors.custom_price ? 'input-error' : '']" step="0.01" min="0" placeholder="Override room type price" />
                <p v-if="fieldErrors.custom_price" class="text-xs text-red-500 mt-1">{{ fieldErrors.custom_price }}</p>
              </div>
              <div>
                <label class="label">Notes</label>
                <textarea v-model="roomForm.notes" class="input" rows="2" placeholder="Any special notes"></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
                {{ isSubmitting ? 'Adding...' : 'Add Room' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>
