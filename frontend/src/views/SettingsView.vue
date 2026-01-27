<script setup>
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold">Settings</h1>
      <p class="text-secondary">Configure hotel and theme settings</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Theme Settings -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Theme Settings</h2>
        <div class="space-y-4">
          <div>
            <label class="label">Theme Mode</label>
            <div class="flex space-x-2">
              <button
                @click="themeStore.setThemeMode('light')"
                :class="['btn', themeStore.themeMode === 'light' ? 'btn-primary' : 'btn-secondary']"
              >Light</button>
              <button
                @click="themeStore.setThemeMode('dark')"
                :class="['btn', themeStore.themeMode === 'dark' ? 'btn-primary' : 'btn-secondary']"
              >Dark</button>
              <button
                @click="themeStore.setThemeMode('system')"
                :class="['btn', themeStore.themeMode === 'system' ? 'btn-primary' : 'btn-secondary']"
              >System</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Hotel Settings -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Hotel Settings</h2>
        <p class="text-secondary">Hotel configuration options will appear here</p>
      </div>
    </div>
  </div>
</template>
