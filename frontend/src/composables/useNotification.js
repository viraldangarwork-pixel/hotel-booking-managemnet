/**
 * Composable for showing notifications/toasts
 */
import { ref, readonly } from 'vue'

const notifications = ref([])
let notificationId = 0

export function useNotification() {
  function show(message, type = 'info', duration = 5000) {
    const id = ++notificationId

    const notification = {
      id,
      message,
      type, // 'success' | 'error' | 'warning' | 'info'
      duration,
    }

    notifications.value.push(notification)

    if (duration > 0) {
      setTimeout(() => {
        remove(id)
      }, duration)
    }

    return id
  }

  function success(message, duration = 5000) {
    return show(message, 'success', duration)
  }

  function error(message, duration = 8000) {
    return show(message, 'error', duration)
  }

  function warning(message, duration = 6000) {
    return show(message, 'warning', duration)
  }

  function info(message, duration = 5000) {
    return show(message, 'info', duration)
  }

  function remove(id) {
    const index = notifications.value.findIndex((n) => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  function clear() {
    notifications.value = []
  }

  return {
    notifications: readonly(notifications),
    show,
    success,
    error,
    warning,
    info,
    remove,
    clear,
  }
}
