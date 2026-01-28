<script setup>
import { ref, onMounted } from 'vue'
import { useRoomsStore } from '@/stores/rooms'

const roomsStore = useRoomsStore()

const showAddModal = ref(false)
const isSubmitting = ref(false)
const formError = ref('')
const roomForm = ref({
  room_number: '',
  floor: 1,
  room_type_id: '',
  custom_price: '',
  notes: '',
})

onMounted(() => {
  roomsStore.fetchRooms()
  roomsStore.fetchRoomTypes()
})

const getStatusColor = (status) => {
  const colors = {
    available: 'bg-green-500',
    booked: 'bg-blue-500',
    checked_in: 'bg-yellow-500',
    maintenance: 'bg-red-500',
    cleaning: 'bg-orange-500'
  }
  return colors[status] || 'bg-gray-500'
}

function openAddModal() {
  roomForm.value = { room_number: '', floor: 1, room_type_id: '', custom_price: '', notes: '' }
  formError.value = ''
  showAddModal.value = true
}

function closeModal() {
  showAddModal.value = false
  formError.value = ''
}

async function handleAddRoom() {
  formError.value = ''
  if (!roomForm.value.room_number) { formError.value = 'Room number is required'; return }
  if (!roomForm.value.room_type_id) { formError.value = 'Room type is required'; return }

  isSubmitting.value = true
  const payload = {
    room_number: roomForm.value.room_number,
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
  } else {
    formError.value = result.error
  }
}

async function handleStatusChange(roomId, newStatus) {
  await roomsStore.updateRoomStatus(roomId, newStatus)
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Rooms</h1>
        <p class="text-secondary">Manage hotel rooms and availability</p>
      </div>
      <button class="btn btn-primary" @click="openAddModal">+ Add Room</button>
    </div>

    <!-- Room status summary -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <div v-for="(count, status) in roomsStore.roomsByStatus" :key="status" class="card text-center">
        <div class="flex items-center justify-center space-x-2">
          <span :class="['w-3 h-3 rounded-full', getStatusColor(status)]"></span>
          <span class="capitalize">{{ status.replace('_', ' ') }}</span>
        </div>
        <p class="text-2xl font-bold mt-2">{{ count }}</p>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="roomsStore.isLoading" class="text-center py-12">
      <p class="text-secondary">Loading rooms...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="roomsStore.rooms.length === 0" class="card text-center py-12">
      <p class="text-secondary mb-4">No rooms found. Add your first room to get started.</p>
      <button class="btn btn-primary" @click="openAddModal">+ Add Room</button>
    </div>

    <!-- Rooms grid by floor -->
    <div v-else v-for="(rooms, floor) in roomsStore.roomsByFloor" :key="floor" class="card">
      <h3 class="text-lg font-semibold mb-4">Floor {{ floor }}</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div
          v-for="room in rooms"
          :key="room.id"
          class="p-4 rounded-lg border-2 cursor-pointer hover:shadow-md transition-shadow relative group"
          :class="{
            'border-green-500 bg-green-50 dark:bg-green-900/20': room.status === 'available',
            'border-blue-500 bg-blue-50 dark:bg-blue-900/20': room.status === 'booked',
            'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20': room.status === 'checked_in',
            'border-red-500 bg-red-50 dark:bg-red-900/20': room.status === 'maintenance',
            'border-orange-500 bg-orange-50 dark:bg-orange-900/20': room.status === 'cleaning'
          }"
        >
          <p class="font-bold text-lg">{{ room.room_number }}</p>
          <p class="text-sm text-secondary">{{ room.room_type?.name || 'N/A' }}</p>
          <span class="text-xs capitalize">{{ room.status.replace('_', ' ') }}</span>

          <!-- Quick status change -->
          <div class="hidden group-hover:block absolute top-1 right-1">
            <select
              class="text-xs rounded border border-gray-300 dark:border-gray-600 dark:bg-gray-700 p-0.5"
              :value="room.status"
              @change="handleStatusChange(room.id, $event.target.value)"
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
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <form @submit.prevent="handleAddRoom">
            <div class="modal-body">
              <div v-if="formError" class="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-md text-sm">
                {{ formError }}
              </div>
              <div>
                <label class="label">Room Number *</label>
                <input v-model="roomForm.room_number" type="text" class="input" placeholder="e.g. 101" required />
              </div>
              <div>
                <label class="label">Floor *</label>
                <input v-model.number="roomForm.floor" type="number" class="input" min="1" required />
              </div>
              <div>
                <label class="label">Room Type *</label>
                <select v-model="roomForm.room_type_id" class="select" required>
                  <option value="" disabled>Select room type</option>
                  <option v-for="rt in roomsStore.roomTypes" :key="rt.id" :value="rt.id">
                    {{ rt.name }} - ${{ rt.base_price }}/night
                  </option>
                </select>
              </div>
              <div>
                <label class="label">Custom Price (optional)</label>
                <input v-model="roomForm.custom_price" type="number" class="input" step="0.01" min="0" placeholder="Override room type price" />
              </div>
              <div>
                <label class="label">Notes</label>
                <textarea v-model="roomForm.notes" class="input" rows="2" placeholder="Any special notes about this room"></textarea>
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
