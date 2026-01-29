<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()

const activeTab = ref('ai')
const messageInput = ref('')
const chatContainer = ref(null)
const suggestions = [
  'Show available rooms',
  "Today's check-ins",
  "Today's check-outs",
  'Current occupancy',
  'Total guests',
  'Revenue summary',
]

onMounted(async () => {
  await Promise.all([
    chatStore.fetchSessions(),
    chatStore.fetchDataSummary(),
  ])
  // Auto-create a session if none exists
  if (chatStore.sessions.length === 0) {
    await chatStore.createSession()
  } else {
    await chatStore.loadSession(chatStore.sessions[0].id)
  }
})

async function sendMessage() {
  const content = messageInput.value.trim()
  if (!content || chatStore.isSending) return
  messageInput.value = ''
  await chatStore.sendMessage(content)
  await nextTick()
  scrollToBottom()
  // Refresh data summary after a query
  chatStore.fetchDataSummary()
}

async function useSuggestion(text) {
  messageInput.value = text
  await sendMessage()
}

function scrollToBottom() {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

async function startNewSession() {
  await chatStore.createSession()
}

async function switchSession(session) {
  await chatStore.loadSession(session.id)
  await nextTick()
  scrollToBottom()
}

async function removeSession(sessionId) {
  await chatStore.deleteSession(sessionId)
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

function formatMessageContent(content) {
  return content
    .replace(/\n- /g, '\n&bull; ')
    .replace(/\n/g, '<br>')
}

const dataSummary = computed(() => chatStore.dataSummary)
const occupancyRate = computed(() => {
  if (!dataSummary.value?.rooms?.total) return 0
  const { occupied, booked, total } = dataSummary.value.rooms
  return Math.round(((occupied + booked) / total) * 100)
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <div>
      <h1 class="text-2xl font-bold">Chat & Data Panel</h1>
      <p class="text-secondary">AI assistant for hotel data access</p>
    </div>

    <!-- Tabs -->
    <div class="tab-group">
      <button
        @click="activeTab = 'ai'"
        :class="['tab', activeTab === 'ai' ? 'tab-active' : '']"
      >
        <svg class="w-4 h-4 mr-1.5 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 3.104v5.714a2.25 2.25 0 0 1-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 0 1 4.5 0m0 0v5.714a2.25 2.25 0 0 0 .659 1.591L19 14.5M14.25 3.104c.251.023.501.05.75.082M19 14.5l-2.47 5.527a.5.5 0 0 1-.457.298H7.927a.5.5 0 0 1-.457-.298L5 14.5m14 0H5" />
        </svg>
        AI Assistant
      </button>
      <button
        @click="activeTab = 'data'"
        :class="['tab', activeTab === 'data' ? 'tab-active' : '']"
      >
        <svg class="w-4 h-4 mr-1.5 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        Data Panel
      </button>
    </div>

    <!-- AI Assistant Tab -->
    <div v-if="activeTab === 'ai'" class="grid grid-cols-1 lg:grid-cols-4 gap-6 animate-slide-up">
      <!-- Session Sidebar -->
      <div class="lg:col-span-1">
        <div class="card !p-3">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-semibold">Sessions</h3>
            <button
              class="btn-icon text-primary-600"
              @click="startNewSession"
              title="New session"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
          <div class="space-y-1 max-h-[400px] overflow-y-auto">
            <div
              v-for="session in chatStore.sessions"
              :key="session.id"
              @click="switchSession(session)"
              :class="[
                'flex items-center justify-between p-2 rounded-lg cursor-pointer text-sm transition-colors',
                chatStore.currentSession?.id === session.id
                  ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700'
              ]"
            >
              <span class="truncate">Session #{{ session.id }}</span>
              <button
                class="text-gray-400 hover:text-red-500 flex-shrink-0 ml-2"
                @click.stop="removeSession(session.id)"
                title="Delete session"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <p v-if="chatStore.sessions.length === 0" class="text-xs text-secondary text-center py-4">
              No sessions yet
            </p>
          </div>
        </div>

        <!-- Quick Stats Card -->
        <div v-if="dataSummary" class="card !p-3 mt-4">
          <h3 class="text-sm font-semibold mb-3">Quick Stats</h3>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-secondary">Available Rooms</span>
              <span class="font-medium text-green-600">{{ dataSummary.rooms.available }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-secondary">Occupied</span>
              <span class="font-medium text-blue-600">{{ dataSummary.rooms.occupied }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-secondary">Today Check-ins</span>
              <span class="font-medium text-orange-600">{{ dataSummary.today.check_in_count }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-secondary">Today Check-outs</span>
              <span class="font-medium text-purple-600">{{ dataSummary.today.check_out_count }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Chat Area -->
      <div class="lg:col-span-3 card !p-0 flex flex-col" style="min-height: 550px;">
        <!-- Chat Header -->
        <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
              <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 3.104v5.714a2.25 2.25 0 0 1-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 0 1 4.5 0m0 0v5.714a2.25 2.25 0 0 0 .659 1.591L19 14.5M14.25 3.104c.251.023.501.05.75.082M19 14.5l-2.47 5.527a.5.5 0 0 1-.457.298H7.927a.5.5 0 0 1-.457-.298L5 14.5m14 0H5" />
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-semibold">Hotel AI Assistant</h3>
              <p class="text-xs text-secondary">Ask about rooms, bookings, guests</p>
            </div>
          </div>
        </div>

        <!-- Messages -->
        <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
          <!-- Welcome message if no messages -->
          <div v-if="chatStore.messages.length === 0" class="text-center py-8">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-primary-50 dark:bg-primary-900/20 flex items-center justify-center">
              <svg class="w-8 h-8 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h4 class="text-lg font-semibold mb-2">Hotel Data Assistant</h4>
            <p class="text-secondary text-sm mb-6 max-w-md mx-auto">
              Ask me anything about your hotel data — room availability, bookings, guest info, occupancy rates, and more.
            </p>
            <div class="flex flex-wrap justify-center gap-2">
              <button
                v-for="suggestion in suggestions"
                :key="suggestion"
                @click="useSuggestion(suggestion)"
                class="px-3 py-1.5 text-sm rounded-full border border-gray-300 dark:border-gray-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 hover:border-primary-300 dark:hover:border-primary-600 transition-colors"
              >
                {{ suggestion }}
              </button>
            </div>
          </div>

          <!-- Chat messages -->
          <template v-for="msg in chatStore.messages" :key="msg.id">
            <div :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
              <div :class="[
                'chat-bubble',
                msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'
              ]">
                <div v-if="msg.role === 'assistant'" v-html="formatMessageContent(msg.content)"></div>
                <div v-else>{{ msg.content }}</div>
                <div :class="['text-xs mt-1', msg.role === 'user' ? 'text-primary-200' : 'text-gray-400']">
                  {{ formatTime(msg.created_at) }}
                </div>
              </div>
            </div>
          </template>

          <!-- Typing indicator -->
          <div v-if="chatStore.isSending" class="flex justify-start">
            <div class="chat-bubble chat-bubble-assistant">
              <div class="flex items-center gap-1">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Suggestion chips (when messages exist) -->
        <div v-if="chatStore.messages.length > 0 && !chatStore.isSending" class="px-4 pb-2">
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="suggestion in suggestions"
              :key="suggestion"
              @click="useSuggestion(suggestion)"
              class="px-2.5 py-1 text-xs rounded-full border border-gray-200 dark:border-gray-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>

        <!-- Input area -->
        <div class="border-t border-gray-200 dark:border-gray-700 p-3">
          <form @submit.prevent="sendMessage" class="flex gap-2">
            <input
              v-model="messageInput"
              type="text"
              class="input flex-1"
              placeholder="Ask about rooms, bookings, guests..."
              :disabled="chatStore.isSending || !chatStore.currentSession"
            />
            <button
              type="submit"
              class="btn btn-primary !px-4"
              :disabled="!messageInput.trim() || chatStore.isSending || !chatStore.currentSession"
            >
              <svg v-if="chatStore.isSending" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- Data Panel Tab -->
    <div v-if="activeTab === 'data'" class="animate-slide-up">
      <!-- Loading -->
      <div v-if="chatStore.isLoadingData" class="text-center py-12">
        <div class="spinner mx-auto mb-3"></div>
        <p class="text-secondary">Loading data...</p>
      </div>

      <div v-else-if="dataSummary" class="space-y-6">
        <!-- Room Status Overview -->
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div class="card !p-4 text-center card-hover">
            <div class="text-3xl font-bold text-blue-600">{{ dataSummary.rooms.total }}</div>
            <div class="text-sm text-secondary mt-1">Total Rooms</div>
          </div>
          <div class="card !p-4 text-center card-hover">
            <div class="text-3xl font-bold text-green-600">{{ dataSummary.rooms.available }}</div>
            <div class="text-sm text-secondary mt-1">Available</div>
          </div>
          <div class="card !p-4 text-center card-hover">
            <div class="text-3xl font-bold text-orange-600">{{ dataSummary.rooms.occupied }}</div>
            <div class="text-sm text-secondary mt-1">Occupied</div>
          </div>
          <div class="card !p-4 text-center card-hover">
            <div class="text-3xl font-bold text-purple-600">{{ dataSummary.rooms.booked }}</div>
            <div class="text-sm text-secondary mt-1">Booked</div>
          </div>
          <div class="card !p-4 text-center card-hover">
            <div class="text-3xl font-bold text-red-600">{{ dataSummary.rooms.maintenance }}</div>
            <div class="text-sm text-secondary mt-1">Maintenance</div>
          </div>
        </div>

        <!-- Occupancy Bar -->
        <div class="card">
          <h3 class="text-lg font-semibold mb-3">Occupancy Rate</h3>
          <div class="flex items-center gap-4">
            <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-1000"
                :class="occupancyRate > 80 ? 'bg-red-500' : occupancyRate > 50 ? 'bg-orange-500' : 'bg-green-500'"
                :style="{ width: occupancyRate + '%' }"
              ></div>
            </div>
            <span class="text-lg font-bold" :class="occupancyRate > 80 ? 'text-red-600' : occupancyRate > 50 ? 'text-orange-600' : 'text-green-600'">
              {{ occupancyRate }}%
            </span>
          </div>
        </div>

        <!-- Today's Activity -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Today's Check-ins -->
          <div class="card">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center">
                <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold">Today's Check-ins ({{ dataSummary.today.check_in_count }})</h3>
            </div>
            <div v-if="dataSummary.today.check_ins.length > 0" class="space-y-2">
              <div
                v-for="(item, idx) in dataSummary.today.check_ins"
                :key="idx"
                class="flex items-center justify-between p-2 rounded-lg bg-gray-50 dark:bg-gray-800 stagger-item"
              >
                <div>
                  <span class="font-medium text-sm">{{ item.guest_name }}</span>
                  <span class="text-xs text-secondary ml-2">Room {{ item.room_number }}</span>
                </div>
                <span class="badge badge-info text-xs">{{ item.booking_ref }}</span>
              </div>
            </div>
            <p v-else class="text-secondary text-sm text-center py-4">No check-ins today</p>
          </div>

          <!-- Today's Check-outs -->
          <div class="card">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-8 h-8 rounded-full bg-purple-100 dark:bg-purple-900/20 flex items-center justify-center">
                <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold">Today's Check-outs ({{ dataSummary.today.check_out_count }})</h3>
            </div>
            <div v-if="dataSummary.today.check_outs.length > 0" class="space-y-2">
              <div
                v-for="(item, idx) in dataSummary.today.check_outs"
                :key="idx"
                class="flex items-center justify-between p-2 rounded-lg bg-gray-50 dark:bg-gray-800 stagger-item"
              >
                <div>
                  <span class="font-medium text-sm">{{ item.guest_name }}</span>
                  <span class="text-xs text-secondary ml-2">Room {{ item.room_number }}</span>
                </div>
                <span class="badge badge-secondary text-xs">{{ item.booking_ref }}</span>
              </div>
            </div>
            <p v-else class="text-secondary text-sm text-center py-4">No check-outs today</p>
          </div>
        </div>

        <!-- Guest & Booking Stats -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="card !p-4 card-hover">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div>
                <div class="text-2xl font-bold">{{ dataSummary.guests.total }}</div>
                <div class="text-sm text-secondary">Total Guests</div>
              </div>
            </div>
          </div>
          <div class="card !p-4 card-hover">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-yellow-100 dark:bg-yellow-900/20 flex items-center justify-center">
                <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
              </div>
              <div>
                <div class="text-2xl font-bold">{{ dataSummary.guests.vip }}</div>
                <div class="text-sm text-secondary">VIP Guests</div>
              </div>
            </div>
          </div>
          <div class="card !p-4 card-hover">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div>
                <div class="text-2xl font-bold">{{ dataSummary.bookings.active }}</div>
                <div class="text-sm text-secondary">Active Bookings</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No data state -->
      <div v-else class="card text-center py-12">
        <p class="text-secondary">Unable to load data summary. Please try again.</p>
        <button class="btn btn-primary mt-4" @click="chatStore.fetchDataSummary()">Retry</button>
      </div>
    </div>
  </div>
</template>
