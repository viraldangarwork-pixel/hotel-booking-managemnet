<script setup>
import { ref } from 'vue'
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  isSidebarOpen: Boolean
})

const emit = defineEmits(['toggle-sidebar', 'toggle-mobile-sidebar', 'logout'])

const themeStore = useThemeStore()
const showUserMenu = ref(false)
</script>

<template>
  <header class="sticky top-0 z-30 bg-card border-b border-gray-200 dark:border-gray-700">
    <div class="flex items-center justify-between h-16 px-4 lg:px-6">
      <!-- Left side -->
      <div class="flex items-center space-x-4">
        <!-- Mobile menu button -->
        <button
          @click="emit('toggle-mobile-sidebar')"
          class="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <!-- Desktop sidebar toggle -->
        <button
          @click="emit('toggle-sidebar')"
          class="hidden lg:block p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
          </svg>
        </button>

        <!-- Search -->
        <div class="hidden md:flex items-center">
          <div class="relative">
            <input
              type="text"
              placeholder="Search..."
              class="w-64 pl-10 pr-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <svg
              class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Right side -->
      <div class="flex items-center space-x-4">
        <!-- Theme toggle -->
        <button
          @click="themeStore.toggleDarkMode()"
          class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          :title="themeStore.isDark ? 'Switch to light mode' : 'Switch to dark mode'"
        >
          <svg v-if="themeStore.isDark" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        </button>

        <!-- Notifications -->
        <button class="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        <!-- User menu -->
        <div class="relative">
          <button
            @click="showUserMenu = !showUserMenu"
            class="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <div class="w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
              <span class="text-primary-600 dark:text-primary-400 font-semibold text-sm">U</span>
            </div>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <!-- Dropdown -->
          <div
            v-if="showUserMenu"
            class="absolute right-0 mt-2 w-48 bg-card rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1"
          >
            <router-link
              to="/settings"
              class="block px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800"
              @click="showUserMenu = false"
            >
              Settings
            </router-link>
            <hr class="my-1 border-gray-200 dark:border-gray-700" />
            <button
              @click="emit('logout'); showUserMenu = false"
              class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>
