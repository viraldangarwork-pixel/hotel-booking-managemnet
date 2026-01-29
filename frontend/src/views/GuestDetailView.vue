<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGuestsStore } from '@/stores/guests'
import { useBookingsStore } from '@/stores/bookings'

const route = useRoute()
const router = useRouter()
const guestsStore = useGuestsStore()
const bookingsStore = useBookingsStore()

const activeTab = ref('profile')
const isUploading = ref(false)
const uploadError = ref('')
const uploadSuccess = ref('')
const showImageViewer = ref(false)
const viewerImageUrl = ref('')
const showEditModal = ref(false)
const isEditing = ref(false)
const editForm = ref({})
const editError = ref('')

// Document upload refs
const frontFileInput = ref(null)
const backFileInput = ref(null)
const documentType = ref('')

const guest = computed(() => guestsStore.currentGuest)

onMounted(async () => {
  await guestsStore.fetchGuest(route.params.id)
  await bookingsStore.fetchBookings({ guest_id: route.params.id })
})

const guestBookings = computed(() => {
  return bookingsStore.bookings.filter(b => b.guest_id === Number(route.params.id))
})

const apiBase = import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || ''

function getImageUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${apiBase}${path}`
}

async function handleFileUpload(side) {
  const input = side === 'front' ? frontFileInput.value : backFileInput.value
  const file = input?.files?.[0]
  if (!file) return

  // Validate file type
  const allowed = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowed.includes(file.type)) {
    uploadError.value = 'Only JPG, PNG and WebP images are allowed'
    return
  }

  // Validate file size (10MB)
  if (file.size > 10 * 1024 * 1024) {
    uploadError.value = 'File size must be under 10MB'
    return
  }

  uploadError.value = ''
  uploadSuccess.value = ''
  isUploading.value = true

  const docType = documentType.value || guest.value?.id_type || ''
  const result = await guestsStore.uploadDocument(guest.value.id, file, side, docType)

  isUploading.value = false

  if (result.success) {
    uploadSuccess.value = `${side === 'front' ? 'Front' : 'Back'} side uploaded. Status: ${result.data.clarity_status}`
    setTimeout(() => { uploadSuccess.value = '' }, 5000)
  } else {
    uploadError.value = result.error
  }

  // Reset file input
  input.value = ''
}

function openImageViewer(url) {
  viewerImageUrl.value = getImageUrl(url)
  showImageViewer.value = true
}

function openEditModal() {
  if (!guest.value) return
  editForm.value = {
    first_name: guest.value.first_name,
    last_name: guest.value.last_name,
    email: guest.value.email || '',
    phone: guest.value.phone,
    whatsapp_number: guest.value.whatsapp_number || '',
    id_type: guest.value.id_type || '',
    id_number: guest.value.id_number || '',
    nationality: guest.value.nationality || '',
    city: guest.value.city || '',
    address: guest.value.address || '',
    notes: guest.value.notes || '',
  }
  editError.value = ''
  showEditModal.value = true
}

async function handleEditGuest() {
  editError.value = ''
  if (!editForm.value.first_name?.trim()) { editError.value = 'First name is required'; return }
  if (!editForm.value.last_name?.trim()) { editError.value = 'Last name is required'; return }
  if (!editForm.value.phone?.trim()) { editError.value = 'Phone is required'; return }

  isEditing.value = true
  const payload = { ...editForm.value }
  Object.keys(payload).forEach(k => { if (payload[k] === '') payload[k] = null })
  payload.first_name = editForm.value.first_name.trim()
  payload.last_name = editForm.value.last_name.trim()
  payload.phone = editForm.value.phone.trim()

  const result = await guestsStore.updateGuest(guest.value.id, payload)
  isEditing.value = false

  if (result.success) {
    showEditModal.value = false
  } else {
    editError.value = result.error
  }
}

async function toggleVIP() {
  if (!guest.value) return
  await guestsStore.toggleVIP(guest.value.id, !guest.value.is_vip)
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatDateTime(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function getStatusBadge(status) {
  const map = { pending: 'badge-warning', confirmed: 'badge-info', checked_in: 'badge-success', checked_out: 'badge-secondary', cancelled: 'badge-error', no_show: 'badge-error' }
  return map[status] || 'badge-secondary'
}

function getClarityBadge(status) {
  if (status === 'clear') return 'badge-clear'
  if (status === 'unclear') return 'badge-unclear'
  return 'badge-pending-doc'
}
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Back button -->
    <button @click="router.push({ name: 'guests' })" class="btn btn-secondary btn-sm">
      <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      Back to Guests
    </button>

    <!-- Loading -->
    <div v-if="guestsStore.isLoading && !guest" class="flex justify-center py-12">
      <div class="spinner"></div>
    </div>

    <template v-if="guest">
      <!-- Guest header -->
      <div class="card animate-slide-down">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="flex items-center space-x-4">
            <div class="w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center flex-shrink-0">
              <span class="text-primary-600 dark:text-primary-400 font-bold text-2xl">
                {{ guest.first_name?.charAt(0) }}{{ guest.last_name?.charAt(0) }}
              </span>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h1 class="text-2xl font-bold">{{ guest.first_name }} {{ guest.last_name }}</h1>
                <span v-if="guest.is_vip" class="badge badge-warning">VIP</span>
                <span v-if="guest.document_clarity_status" :class="['badge', getClarityBadge(guest.document_clarity_status)]">
                  Doc: {{ guest.document_clarity_status }}
                </span>
              </div>
              <div class="flex items-center gap-4 mt-1 text-sm text-secondary">
                <span>{{ guest.phone }}</span>
                <span v-if="guest.email">{{ guest.email }}</span>
                <span v-if="guest.nationality">{{ guest.nationality }}</span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button @click="toggleVIP" :class="['btn btn-sm', guest.is_vip ? 'btn-warning' : 'btn-outline']">
              {{ guest.is_vip ? 'Remove VIP' : 'Mark VIP' }}
            </button>
            <button @click="openEditModal" class="btn btn-sm btn-secondary">Edit Profile</button>
          </div>
        </div>

        <!-- Stats row -->
        <div class="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div class="text-center">
            <p class="text-2xl font-bold text-primary-600">{{ guest.total_stays }}</p>
            <p class="text-xs text-secondary">Total Stays</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold text-green-600">{{ guest.total_spent ? (guest.total_spent / 100).toFixed(0) : 0 }}</p>
            <p class="text-xs text-secondary">Total Spent</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold">{{ guest.last_visit ? formatDate(guest.last_visit) : 'Never' }}</p>
            <p class="text-xs text-secondary">Last Visit</p>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="tab-group w-fit">
        <button @click="activeTab = 'profile'" :class="['tab', activeTab === 'profile' ? 'tab-active' : '']">Profile</button>
        <button @click="activeTab = 'documents'" :class="['tab', activeTab === 'documents' ? 'tab-active' : '']">Documents</button>
        <button @click="activeTab = 'bookings'" :class="['tab', activeTab === 'bookings' ? 'tab-active' : '']">Bookings</button>
      </div>

      <!-- Profile Tab -->
      <div v-if="activeTab === 'profile'" class="card animate-slide-up">
        <h2 class="text-lg font-semibold mb-4">Personal Information</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-y-4 gap-x-8">
          <div><span class="label">Full Name</span><p class="font-medium">{{ guest.first_name }} {{ guest.last_name }}</p></div>
          <div><span class="label">Phone</span><p class="font-medium">{{ guest.phone }}</p></div>
          <div><span class="label">Email</span><p class="font-medium">{{ guest.email || 'N/A' }}</p></div>
          <div><span class="label">WhatsApp</span><p class="font-medium">{{ guest.whatsapp_number || 'N/A' }}</p></div>
          <div><span class="label">ID Type</span><p class="font-medium">{{ guest.id_type || 'N/A' }}</p></div>
          <div><span class="label">ID Number</span><p class="font-medium">{{ guest.id_number || 'N/A' }}</p></div>
          <div><span class="label">Nationality</span><p class="font-medium">{{ guest.nationality || 'N/A' }}</p></div>
          <div><span class="label">City</span><p class="font-medium">{{ guest.city || 'N/A' }}</p></div>
          <div class="md:col-span-2"><span class="label">Address</span><p class="font-medium">{{ guest.address || 'N/A' }}</p></div>
          <div class="md:col-span-2"><span class="label">Notes</span><p class="font-medium">{{ guest.notes || 'None' }}</p></div>
          <div v-if="guest.tags && guest.tags.length > 0" class="md:col-span-2">
            <span class="label">Tags</span>
            <div class="flex flex-wrap gap-2 mt-1">
              <span v-for="tag in guest.tags" :key="tag" class="badge badge-info">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Documents Tab -->
      <div v-if="activeTab === 'documents'" class="space-y-6 animate-slide-up">
        <!-- Upload alerts -->
        <div v-if="uploadError" class="alert alert-error">{{ uploadError }}</div>
        <div v-if="uploadSuccess" class="alert alert-success">{{ uploadSuccess }}</div>

        <!-- Document type selector -->
        <div class="card">
          <h2 class="text-lg font-semibold mb-4">Identity Document</h2>
          <div class="mb-4">
            <label class="label">Document Type</label>
            <select v-model="documentType" class="select max-w-xs">
              <option value="">{{ guest.id_type || 'Select Type' }}</option>
              <option value="passport">Passport</option>
              <option value="drivers_license">Drivers License</option>
              <option value="national_id">National ID</option>
              <option value="aadhar">Aadhar Card</option>
              <option value="voter_id">Voter ID</option>
              <option value="pan_card">PAN Card</option>
            </select>
          </div>

          <!-- Clarity status -->
          <div v-if="guest.document_clarity_status" class="mb-4 p-3 rounded-lg" :class="{
            'bg-green-50 dark:bg-green-900/20': guest.document_clarity_status === 'clear',
            'bg-red-50 dark:bg-red-900/20': guest.document_clarity_status === 'unclear',
            'bg-yellow-50 dark:bg-yellow-900/20': guest.document_clarity_status === 'pending'
          }">
            <div class="flex items-center gap-2 mb-1">
              <span :class="['badge', getClarityBadge(guest.document_clarity_status)]">{{ guest.document_clarity_status }}</span>
              <span class="text-sm font-medium">Document Clarity Check</span>
            </div>
            <p class="text-sm text-secondary">{{ guest.document_clarity_notes }}</p>
          </div>

          <!-- Upload areas -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Front side -->
            <div>
              <h3 class="font-medium mb-2">Front Side</h3>
              <div v-if="guest.id_document_front_url" class="relative group">
                <img
                  :src="getImageUrl(guest.id_document_front_url)"
                  alt="Document Front"
                  class="w-full h-48 object-cover rounded-lg border border-gray-200 dark:border-gray-700 cursor-pointer"
                  @click="openImageViewer(guest.id_document_front_url)"
                />
                <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all rounded-lg flex items-center justify-center">
                  <span class="text-white opacity-0 group-hover:opacity-100 transition-opacity text-sm font-medium">Click to view</span>
                </div>
              </div>
              <div class="mt-2">
                <input ref="frontFileInput" type="file" accept="image/*" class="hidden" @change="handleFileUpload('front')" />
                <button @click="frontFileInput?.click()" :disabled="isUploading" class="upload-zone w-full">
                  <svg class="w-8 h-8 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                  <p class="text-sm">{{ isUploading ? 'Uploading...' : guest.id_document_front_url ? 'Replace front image' : 'Upload front side' }}</p>
                  <p class="text-xs text-secondary mt-1">JPG, PNG or WebP (max 10MB)</p>
                </button>
              </div>
            </div>

            <!-- Back side -->
            <div>
              <h3 class="font-medium mb-2">Back Side</h3>
              <div v-if="guest.id_document_back_url" class="relative group">
                <img
                  :src="getImageUrl(guest.id_document_back_url)"
                  alt="Document Back"
                  class="w-full h-48 object-cover rounded-lg border border-gray-200 dark:border-gray-700 cursor-pointer"
                  @click="openImageViewer(guest.id_document_back_url)"
                />
                <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all rounded-lg flex items-center justify-center">
                  <span class="text-white opacity-0 group-hover:opacity-100 transition-opacity text-sm font-medium">Click to view</span>
                </div>
              </div>
              <div class="mt-2">
                <input ref="backFileInput" type="file" accept="image/*" class="hidden" @change="handleFileUpload('back')" />
                <button @click="backFileInput?.click()" :disabled="isUploading" class="upload-zone w-full">
                  <svg class="w-8 h-8 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                  <p class="text-sm">{{ isUploading ? 'Uploading...' : guest.id_document_back_url ? 'Replace back image' : 'Upload back side' }}</p>
                  <p class="text-xs text-secondary mt-1">JPG, PNG or WebP (max 10MB)</p>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bookings Tab -->
      <div v-if="activeTab === 'bookings'" class="card animate-slide-up">
        <h2 class="text-lg font-semibold mb-4">Booking History</h2>
        <div v-if="guestBookings.length === 0" class="text-center py-8 text-secondary">
          No bookings found for this guest.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-gray-200 dark:border-gray-700" style="background-color: var(--color-surface)">
                <th class="px-4 py-3 text-left text-sm font-semibold">Ref</th>
                <th class="px-4 py-3 text-left text-sm font-semibold">Room</th>
                <th class="px-4 py-3 text-left text-sm font-semibold">Check-in</th>
                <th class="px-4 py-3 text-left text-sm font-semibold">Check-out</th>
                <th class="px-4 py-3 text-left text-sm font-semibold">Status</th>
                <th class="px-4 py-3 text-left text-sm font-semibold">Total</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="booking in guestBookings" :key="booking.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer" @click="router.push({ name: 'booking-detail', params: { id: booking.id } })">
                <td class="px-4 py-3 font-medium text-primary-600">{{ booking.booking_ref }}</td>
                <td class="px-4 py-3">{{ booking.room?.room_number || 'N/A' }}</td>
                <td class="px-4 py-3">{{ formatDate(booking.check_in_date) }}</td>
                <td class="px-4 py-3">{{ formatDate(booking.check_out_date) }}</td>
                <td class="px-4 py-3"><span :class="['badge', getStatusBadge(booking.status)]">{{ booking.status?.replace('_', ' ') }}</span></td>
                <td class="px-4 py-3 font-medium">{{ booking.total_amount }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- Image Viewer -->
    <Teleport to="body">
      <div v-if="showImageViewer" class="image-viewer-overlay" @click="showImageViewer = false">
        <button class="absolute top-4 right-4 text-white hover:text-gray-300" @click="showImageViewer = false">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
        <img :src="viewerImageUrl" alt="Document" />
      </div>
    </Teleport>

    <!-- Edit Modal -->
    <Teleport to="body">
      <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
        <div class="modal-content">
          <div class="modal-header">
            <h2 class="text-lg font-semibold">Edit Guest</h2>
            <button class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" @click="showEditModal = false">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <form @submit.prevent="handleEditGuest">
            <div class="modal-body">
              <div v-if="editError" class="alert alert-error">{{ editError }}</div>
              <div class="grid grid-cols-2 gap-4">
                <div><label class="label">First Name *</label><input v-model="editForm.first_name" type="text" class="input" required /></div>
                <div><label class="label">Last Name *</label><input v-model="editForm.last_name" type="text" class="input" required /></div>
              </div>
              <div><label class="label">Phone *</label><input v-model="editForm.phone" type="tel" class="input" required /></div>
              <div><label class="label">Email</label><input v-model="editForm.email" type="email" class="input" /></div>
              <div><label class="label">WhatsApp</label><input v-model="editForm.whatsapp_number" type="tel" class="input" /></div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="label">ID Type</label>
                  <select v-model="editForm.id_type" class="select">
                    <option value="">Select</option>
                    <option value="passport">Passport</option>
                    <option value="drivers_license">Drivers License</option>
                    <option value="national_id">National ID</option>
                    <option value="aadhar">Aadhar Card</option>
                  </select>
                </div>
                <div><label class="label">ID Number</label><input v-model="editForm.id_number" type="text" class="input" /></div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div><label class="label">Nationality</label><input v-model="editForm.nationality" type="text" class="input" /></div>
                <div><label class="label">City</label><input v-model="editForm.city" type="text" class="input" /></div>
              </div>
              <div><label class="label">Address</label><textarea v-model="editForm.address" class="input" rows="2"></textarea></div>
              <div><label class="label">Notes</label><textarea v-model="editForm.notes" class="input" rows="2"></textarea></div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showEditModal = false">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="isEditing">
                {{ isEditing ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>
