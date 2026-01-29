import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useChatStore = defineStore('chat', () => {
  const sessions = ref([])
  const currentSession = ref(null)
  const messages = ref([])
  const isLoading = ref(false)
  const isSending = ref(false)
  const error = ref(null)

  // Data panel
  const dataSummary = ref(null)
  const isLoadingData = ref(false)

  async function fetchSessions() {
    try {
      isLoading.value = true
      const response = await api.get('/chat/ai/sessions')
      sessions.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load sessions'
    } finally {
      isLoading.value = false
    }
  }

  async function createSession() {
    try {
      const response = await api.post('/chat/ai/sessions')
      currentSession.value = response.data
      messages.value = []
      sessions.value.unshift(response.data)
      return { success: true, data: response.data }
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || 'Failed to create session' }
    }
  }

  async function loadSession(sessionId) {
    try {
      isLoading.value = true
      const response = await api.get(`/chat/ai/sessions/${sessionId}`)
      currentSession.value = response.data
      messages.value = response.data.messages || []
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load session'
    } finally {
      isLoading.value = false
    }
  }

  async function sendMessage(content) {
    if (!currentSession.value) return { success: false, error: 'No active session' }
    try {
      isSending.value = true
      // Add user message optimistically
      messages.value.push({
        id: Date.now(),
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      })

      const response = await api.post(`/chat/ai/sessions/${currentSession.value.id}/message`, {
        content,
      })

      // Add AI response
      messages.value.push({
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.message,
        created_at: new Date().toISOString(),
      })

      return { success: true, data: response.data }
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || 'Failed to send message' }
    } finally {
      isSending.value = false
    }
  }

  async function deleteSession(sessionId) {
    try {
      await api.delete(`/chat/ai/sessions/${sessionId}`)
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      if (currentSession.value?.id === sessionId) {
        currentSession.value = null
        messages.value = []
      }
      return { success: true }
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || 'Failed to delete session' }
    }
  }

  async function fetchDataSummary() {
    try {
      isLoadingData.value = true
      const response = await api.get('/chat/ai/data-summary')
      dataSummary.value = response.data
    } catch (err) {
      console.error('Failed to load data summary:', err)
    } finally {
      isLoadingData.value = false
    }
  }

  return {
    sessions,
    currentSession,
    messages,
    isLoading,
    isSending,
    error,
    dataSummary,
    isLoadingData,
    fetchSessions,
    createSession,
    loadSession,
    sendMessage,
    deleteSession,
    fetchDataSummary,
  }
})
