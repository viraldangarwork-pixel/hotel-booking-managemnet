/**
 * Composable for making API calls with loading and error states
 */
import { ref, computed } from 'vue'
import api from '@/utils/api'

export function useApi() {
  const isLoading = ref(false)
  const error = ref(null)
  const data = ref(null)

  const hasError = computed(() => !!error.value)

  async function get(url, params = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get(url, { params })
      data.value = response.data
      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Request failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  async function post(url, payload = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.post(url, payload)
      data.value = response.data
      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Request failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  async function put(url, payload = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.put(url, payload)
      data.value = response.data
      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Request failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  async function del(url) {
    isLoading.value = true
    error.value = null

    try {
      await api.delete(url)
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Request failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    isLoading,
    error,
    data,
    hasError,
    get,
    post,
    put,
    del,
    clearError,
  }
}
