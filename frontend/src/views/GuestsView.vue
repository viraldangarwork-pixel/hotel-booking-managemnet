<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGuestsStore } from '@/stores/guests'
import { useRouter } from 'vue-router'

const guestsStore = useGuestsStore()
const router = useRouter()

const showAddModal = ref(false)
const isSubmitting = ref(false)
const formError = ref('')
const searchQuery = ref('')
const guestForm = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  whatsapp_number: '',
  id_type: '',
  id_number: '',
  nationality: '',
  address: '',
  city: '',
  country: '',
  notes: '',
})

onMounted(() => {
  guestsStore.fetchGuests()
})

const filteredGuests = computed(() => {
  if (!searchQuery.value) return guestsStore.guests
  const q = searchQuery.value.toLowerCase()
  return guestsStore.guests.filter(g =>
    `${g.first_name} ${g.last_name}`.toLowerCase().includes(q) ||
    (g.email && g.email.toLowerCase().includes(q)) ||
    (g.phone && g.phone.includes(q))
  )
})

function openAddModal() {
  guestForm.value = {
    first_name: '', last_name: '', email: '', phone: '', whatsapp_number: '',
    id_type: '', id_number: '', nationality: '', address: '', city: '', country: '', notes: '',
  }
  formError.value = ''
  showAddModal.value = true
}

function closeModal() {
  showAddModal.value = false
  formError.value = ''
}

async function handleAddGuest() {
  formError.value = ''
  if (!guestForm.value.first_name) { formError.value = 'First name is required'; return }
  if (!guestForm.value.last_name) { formError.value = 'Last name is required'; return }
  if (!guestForm.value.phone) { formError.value = 'Phone number is required'; return }

  isSubmitting.value = true
  const payload = { ...guestForm.value }
  // Remove empty strings
  Object.keys(payload).forEach(k => { if (payload[k] === '') delete payload[k] })
  // Ensure required fields
  payload.first_name = guestForm.value.first_name
  payload.last_name = guestForm.value.last_name
  payload.phone = guestForm.value.phone

  const result = await guestsStore.createGuest(payload)
  isSubmitting.value = false

  if (result.success) {
    closeModal()
  } else {
    formError.value = result.error
  }
}

function viewGuest(guestId) {
  router.push({ name: 'guest-detail', params: { id: guestId } })
}

async function handleSearch() {
  if (searchQuery.value.length >= 2) {
    await guestsStore.fetchGuests({ search: searchQuery.value })
  } else if (searchQuery.value.length === 0) {
    await guestsStore.fetchGuests()
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Guests</h1>
        <p class="text-secondary">Guest CRM and profiles</p>
      </div>
      <button class="btn btn-primary" @click="openAddModal">+ Add Guest</button>
    </div>

    <!-- Search -->
    <div class="card">
      <input
        v-model="searchQuery"
        type="text"
        class="input"
        placeholder="Search guests by name, email or phone..."
        @input="handleSearch"
      />
    </div>

    <!-- Loading state -->
    <div v-if="guestsStore.isLoading" class="text-center py-12">
      <p class="text-secondary">Loading guests...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="filteredGuests.length === 0" class="card text-center py-12">
      <p class="text-secondary mb-4">No guests found. Add your first guest to get started.</p>
      <button class="btn btn-primary" @click="openAddModal">+ Add Guest</button>
    </div>

    <!-- Guests grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="guest in filteredGuests"
        :key="guest.id"
        class="card cursor-pointer"
        @click="viewGuest(guest.id)"
      >
        <div class="flex items-start space-x-4">
          <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center flex-shrink-0">
            <span class="text-primary-600 dark:text-primary-400 font-semibold text-lg">
              {{ guest.first_name?.charAt(0) }}{{ guest.last_name?.charAt(0) }}
            </span>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center space-x-2">
              <h3 class="font-semibold truncate">{{ guest.first_name }} {{ guest.last_name }}</h3>
              <span v-if="guest.is_vip" class="badge badge-warning">VIP</span>
            </div>
            <p class="text-sm text-secondary truncate">{{ guest.email || 'No email' }}</p>
            <p class="text-sm text-secondary">{{ guest.phone }}</p>
            <div class="mt-2 text-sm">
              <span class="text-secondary">{{ guest.total_stays || 0 }} stays</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Guest Modal -->
    <Teleport to="body">
      <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2 class="text-lg font-semibold">Add New Guest</h2>
            <button class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" @click="closeModal">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <form @submit.prevent="handleAddGuest">
            <div class="modal-body">
              <div v-if="formError" class="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-md text-sm">
                {{ formError }}
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="label">First Name *</label>
                  <input v-model="guestForm.first_name" type="text" class="input" placeholder="John" required />
                </div>
                <div>
                  <label class="label">Last Name *</label>
                  <input v-model="guestForm.last_name" type="text" class="input" placeholder="Doe" required />
                </div>
              </div>
              <div>
                <label class="label">Phone *</label>
                <input v-model="guestForm.phone" type="tel" class="input" placeholder="+1234567890" required />
              </div>
              <div>
                <label class="label">Email</label>
                <input v-model="guestForm.email" type="email" class="input" placeholder="john@example.com" />
              </div>
              <div>
                <label class="label">WhatsApp Number</label>
                <input v-model="guestForm.whatsapp_number" type="tel" class="input" placeholder="+1234567890" />
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="label">ID Type</label>
                  <select v-model="guestForm.id_type" class="select">
                    <option value="">Select</option>
                    <option value="passport">Passport</option>
                    <option value="drivers_license">Drivers License</option>
                    <option value="national_id">National ID</option>
                    <option value="aadhar">Aadhar</option>
                  </select>
                </div>
                <div>
                  <label class="label">ID Number</label>
                  <input v-model="guestForm.id_number" type="text" class="input" placeholder="ID Number" />
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="label">Nationality</label>
                  <input v-model="guestForm.nationality" type="text" class="input" placeholder="Country" />
                </div>
                <div>
                  <label class="label">City</label>
                  <input v-model="guestForm.city" type="text" class="input" placeholder="City" />
                </div>
              </div>
              <div>
                <label class="label">Address</label>
                <textarea v-model="guestForm.address" class="input" rows="2" placeholder="Full address"></textarea>
              </div>
              <div>
                <label class="label">Notes</label>
                <textarea v-model="guestForm.notes" class="input" rows="2" placeholder="Any notes about this guest"></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
                {{ isSubmitting ? 'Adding...' : 'Add Guest' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>
