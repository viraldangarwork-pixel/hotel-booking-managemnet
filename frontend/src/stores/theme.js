import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import api from '@/utils/api'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(false)
  const themeMode = ref(localStorage.getItem('themeMode') || 'system')
  const themeSettings = ref(null)
  const isLoading = ref(false)

  const hotelId = import.meta.env.VITE_HOTEL_ID || 1

  // Computed theme based on mode
  const computedTheme = computed(() => {
    if (themeMode.value === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return themeMode.value
  })

  // Initialize theme
  function initTheme() {
    // Set initial dark mode based on preference
    updateDarkMode()

    // Watch for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (themeMode.value === 'system') {
        isDark.value = e.matches
      }
    })

    // Load theme settings from backend
    loadThemeSettings()
  }

  function updateDarkMode() {
    isDark.value = computedTheme.value === 'dark'
  }

  function setThemeMode(mode) {
    themeMode.value = mode
    localStorage.setItem('themeMode', mode)
    updateDarkMode()
  }

  function toggleDarkMode() {
    if (themeMode.value === 'system') {
      setThemeMode(isDark.value ? 'light' : 'dark')
    } else {
      setThemeMode(isDark.value ? 'light' : 'dark')
    }
  }

  async function loadThemeSettings() {
    try {
      isLoading.value = true
      const response = await api.get(`/settings/theme/${hotelId}`)
      themeSettings.value = response.data
      applyThemeSettings()
    } catch (error) {
      console.error('Failed to load theme settings:', error)
    } finally {
      isLoading.value = false
    }
  }

  async function updateThemeSettings(settings) {
    try {
      const response = await api.put(`/settings/theme/${hotelId}`, settings)
      themeSettings.value = response.data
      applyThemeSettings()
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to update theme'
      }
    }
  }

  function applyThemeSettings() {
    if (!themeSettings.value) return

    const root = document.documentElement
    const settings = themeSettings.value

    // Apply colors
    root.style.setProperty('--color-primary', settings.primary_color)
    root.style.setProperty('--color-secondary', settings.secondary_color)
    root.style.setProperty('--color-accent', settings.accent_color)
    root.style.setProperty('--color-success', settings.success_color)
    root.style.setProperty('--color-warning', settings.warning_color)
    root.style.setProperty('--color-error', settings.error_color)

    // Apply typography
    root.style.setProperty('--font-family', settings.font_family)
    root.style.setProperty('--font-size-base', settings.font_size_base)

    // Apply border radius
    root.style.setProperty('--border-radius-sm', settings.border_radius_sm)
    root.style.setProperty('--border-radius-md', settings.border_radius_md)
    root.style.setProperty('--border-radius-lg', settings.border_radius_lg)
    root.style.setProperty('--border-radius-xl', settings.border_radius_xl)

    // Apply shadows
    root.style.setProperty('--shadow-sm', settings.shadow_sm)
    root.style.setProperty('--shadow-md', settings.shadow_md)
    root.style.setProperty('--shadow-lg', settings.shadow_lg)

    // Apply light mode backgrounds
    if (!isDark.value) {
      root.style.setProperty('--color-background', settings.background_color)
      root.style.setProperty('--color-surface', settings.surface_color)
      root.style.setProperty('--color-card', settings.card_color)
      root.style.setProperty('--color-text-primary', settings.text_primary)
      root.style.setProperty('--color-text-secondary', settings.text_secondary)
    } else {
      root.style.setProperty('--color-background', settings.dark_background)
      root.style.setProperty('--color-surface', settings.dark_surface)
      root.style.setProperty('--color-card', settings.dark_card)
      root.style.setProperty('--color-text-primary', settings.dark_text_primary)
      root.style.setProperty('--color-text-secondary', settings.dark_text_secondary)
    }

    // Apply custom CSS if exists
    if (settings.custom_css) {
      let customStyle = document.getElementById('custom-theme-css')
      if (!customStyle) {
        customStyle = document.createElement('style')
        customStyle.id = 'custom-theme-css'
        document.head.appendChild(customStyle)
      }
      customStyle.textContent = settings.custom_css
    }
  }

  // Re-apply theme settings when dark mode changes
  watch(isDark, () => {
    applyThemeSettings()
  })

  return {
    isDark,
    themeMode,
    themeSettings,
    isLoading,
    initTheme,
    setThemeMode,
    toggleDarkMode,
    loadThemeSettings,
    updateThemeSettings
  }
})
