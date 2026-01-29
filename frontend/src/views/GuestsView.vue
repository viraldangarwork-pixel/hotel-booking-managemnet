<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGuestsStore } from '@/stores/guests'
import { useRouter } from 'vue-router'

const guestsStore = useGuestsStore()
const router = useRouter()

const showAddModal = ref(false)
const isSubmitting = ref(false)
const formError = ref('')
const successMsg = ref('')
const searchQuery = ref('')
const filterVIP = ref(false)

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

// Validation errors
const fieldErrors = ref({})

onMounted(() => {
  guestsStore.fetchGuests()
})

const filteredGuests = computed(() => {
  let list = guestsStore.guests
  if (filterVIP.value) {
    list = list.filter(g => g.is_vip)
  }
  if (!searchQuery.value) return list
  const q = searchQuery.value.toLowerCase()
  return list.filter(g =>
    `${g.first_name} ${g.last_name}`.toLowerCase().includes(q) ||
    (g.email && g.email.toLowerCase().includes(q)) ||
    (g.phone && g.phone.includes(q))
  )
})

function validateForm() {
  fieldErrors.value = {}
  if (!guestForm.value.first_name.trim()) {
    fieldErrors.value.first_name = 'First name is required'
  }
  if (!guestForm.value.last_name.trim()) {
    fieldErrors.value.last_name = 'Last name is required'
  }
  if (!guestForm.value.phone.trim()) {
    fieldErrors.value.phone = 'Phone number is required'
  } else if (!/^\+?[\d\s-]{7,20}$/.test(guestForm.value.phone.trim())) {
    fieldErrors.value.phone = 'Enter a valid phone number'
  }
  if (guestForm.value.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(guestForm.value.email)) {
    fieldErrors.value.email = 'Enter a valid email address'
  }
  return Object.keys(fieldErrors.value).length === 0
}

function openAddModal() {
  guestForm.value = {
    first_name: '', last_name: '', email: '', phone: '', whatsapp_number: '',
    id_type: '', id_number: '', nationality: '', address: '', city: '', country: '', notes: '',
  }
  formError.value = ''
  fieldErrors.value = {}
  showAddModal.value = true
}

function closeModal() {
  showAddModal.value = false
  formError.value = ''
  fieldErrors.value = {}
}

async function handleAddGuest() {
  formError.value = ''
  if (!validateForm()) {
    formError.value = 'Please fix the errors below'
    return
  }

  isSubmitting.value = true
  const payload = { ...guestForm.value }
  Object.keys(payload).forEach(k => { if (payload[k] === '') delete payload[k] })
  payload.first_name = guestForm.value.first_name.trim()
  payload.last_name = guestForm.value.last_name.trim()
  payload.phone = guestForm.value.phone.trim()

  const result = await guestsStore.createGuest(payload)
  isSubmitting.value = false

  if (result.success) {
    closeModal()
    successMsg.value = `Guest ${result.data.first_name} ${result.data.last_name} added successfully`
    setTimeout(() => { successMsg.value = '' }, 3000)
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

function getDocStatusBadge(guest) {
  if (!guest.id_document_front_url) return null
  if (guest.document_clarity_status === 'clear') return 'badge-clear'
  if (guest.document_clarity_status === 'unclear') return 'badge-unclear'
  return 'badge-pending-doc'
}
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Guests</h1>
        <p class="text-secondary">Guest CRM and profiles</p>
      </div>
      <button class="btn btn-primary" @click="openAddModal">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        Add Guest
      </button>
    </div>

    <!-- Success message -->
    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>

    <!-- Search and filters -->
    <div class="card animate-slide-down">
      <div class="flex flex-col md:flex-row md:items-center gap-4">
        <div class="flex-1 relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          <input
            v-model="searchQuery"
            type="text"
            class="input pl-10"
            placeholder="Search guests by name, email or phone..."
            @input="handleSearch"
          />
        </div>
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="filterVIP" type="checkbox" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
          <span class="text-sm font-medium">VIP Only</span>
        </label>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="guestsStore.isLoading" class="flex justify-center py-12">
      <div class="spinner"></div>
    </div>

    <!-- Empty state -->
    <div v-else-if="filteredGuests.length === 0" class="card text-center py-12 animate-slide-up">
      <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
      <p class="text-secondary mb-4">No guests found. Add your first guest to get started.</p>
      <button class="btn btn-primary" @click="openAddModal">+ Add Guest</button>
    </div>

    <!-- Guests grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="(guest, idx) in filteredGuests"
        :key="guest.id"
        class="card card-hover cursor-pointer stagger-item"
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
            <div class="mt-2 flex items-center gap-2 text-sm">
              <span class="text-secondary">{{ guest.total_stays || 0 }} stays</span>
              <span v-if="guest.id_type" class="badge badge-info">{{ guest.id_type }}</span>
              <span v-if="getDocStatusBadge(guest)" :class="['badge', getDocStatusBadge(guest)]">
                {{ guest.document_clarity_status === 'clear' ? 'Doc OK' : guest.document_clarity_status === 'unclear' ? 'Doc Unclear' : 'Doc Pending' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Guest Modal -->
    <Teleport to="body">
      <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content-wide">
          <div class="modal-header">
            <h2 class="text-lg font-semibold">Add New Guest</h2>
            <button class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" @click="closeModal">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <form @submit.prevent="handleAddGuest">
            <div class="modal-body">
              <div v-if="formError" class="alert alert-error">{{ formError }}</div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="label">First Name *</label>
                  <input v-model="guestForm.first_name" type="text" :class="['input', fieldErrors.first_name ? 'input-error' : '']" placeholder="John" />
                  <p v-if="fieldErrors.first_name" class="text-xs text-red-500 mt-1">{{ fieldErrors.first_name }}</p>
                </div>
                <div>
                  <label class="label">Last Name *</label>
                  <input v-model="guestForm.last_name" type="text" :class="['input', fieldErrors.last_name ? 'input-error' : '']" placeholder="Doe" />
                  <p v-if="fieldErrors.last_name" class="text-xs text-red-500 mt-1">{{ fieldErrors.last_name }}</p>
                </div>
              </div>

              <div>
                <label class="label">Phone *</label>
                <input v-model="guestForm.phone" type="tel" :class="['input', fieldErrors.phone ? 'input-error' : '']" placeholder="+1234567890" />
                <p v-if="fieldErrors.phone" class="text-xs text-red-500 mt-1">{{ fieldErrors.phone }}</p>
              </div>

              <div>
                <label class="label">Email</label>
                <input v-model="guestForm.email" type="email" :class="['input', fieldErrors.email ? 'input-error' : '']" placeholder="john@example.com" />
                <p v-if="fieldErrors.email" class="text-xs text-red-500 mt-1">{{ fieldErrors.email }}</p>
              </div>

              <div>
                <label class="label">WhatsApp Number</label>
                <input v-model="guestForm.whatsapp_number" type="tel" class="input" placeholder="+1234567890" />
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="label">ID Document Type</label>
                  <select v-model="guestForm.id_type" class="select">
                    <option value="">Select Type</option>
                    <option value="passport">Passport</option>
                    <option value="drivers_license">Drivers License</option>
                    <option value="national_id">National ID</option>
                    <option value="aadhar">Aadhar Card</option>
                    <option value="voter_id">Voter ID</option>
                    <option value="pan_card">PAN Card</option>
                  </select>
                </div>
                <div>
                  <label class="label">ID Number</label>
                  <input v-model="guestForm.id_number" type="text" class="input" placeholder="Document Number" />
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

              <p class="text-xs text-secondary">* You can upload identity documents after creating the guest profile.</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
                <span v-if="isSubmitting" class="spinner-sm mr-2"></span>
                {{ isSubmitting ? 'Adding...' : 'Add Guest' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>
