<script setup>
import { onMounted, watch } from 'vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

onMounted(() => {
  themeStore.initTheme()
})

watch(() => themeStore.isDark, (isDark) => {
  if (isDark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
})
</script>

<template>
  <router-view />
</template>

<style>
/* Global styles handled in main.css */
</style>
