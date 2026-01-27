<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import SidebarNav from '@/components/common/SidebarNav.vue'
import TopBar from '@/components/common/TopBar.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const isSidebarOpen = ref(true)
const isMobileSidebarOpen = ref(false)

function toggleSidebar() {
  isSidebarOpen.value = !isSidebarOpen.value
}

function toggleMobileSidebar() {
  isMobileSidebarOpen.value = !isMobileSidebarOpen.value
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Mobile sidebar backdrop -->
    <div
      v-if="isMobileSidebarOpen"
      class="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
      @click="toggleMobileSidebar"
    />

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-50 flex flex-col bg-card border-r border-gray-200 dark:border-gray-700 transition-all duration-300',
        isSidebarOpen ? 'w-64' : 'w-20',
        isMobileSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      ]"
    >
      <!-- Logo -->
      <div class="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
        <div v-if="isSidebarOpen" class="flex items-center space-x-2">
          <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-lg">H</span>
          </div>
          <span class="font-semibold text-lg">Hotel MS</span>
        </div>
        <div v-else class="w-full flex justify-center">
          <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-lg">H</span>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <SidebarNav :collapsed="!isSidebarOpen" />

      <!-- User section -->
      <div class="mt-auto p-4 border-t border-gray-200 dark:border-gray-700">
        <div v-if="isSidebarOpen" class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
            <span class="text-primary-600 dark:text-primary-400 font-semibold">
              {{ authStore.user?.full_name?.charAt(0) || 'U' }}
            </span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium truncate">{{ authStore.user?.full_name }}</p>
            <p class="text-xs text-secondary truncate">{{ authStore.user?.email }}</p>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <div
      :class="[
        'transition-all duration-300',
        isSidebarOpen ? 'lg:ml-64' : 'lg:ml-20'
      ]"
    >
      <!-- Top bar -->
      <TopBar
        :is-sidebar-open="isSidebarOpen"
        @toggle-sidebar="toggleSidebar"
        @toggle-mobile-sidebar="toggleMobileSidebar"
        @logout="logout"
      />

      <!-- Page content -->
      <main class="p-4 lg:p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>
