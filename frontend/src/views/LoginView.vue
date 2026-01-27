<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

async function handleSubmit() {
  error.value = ''
  isLoading.value = true

  const result = await authStore.login(email.value, password.value)

  if (result.success) {
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } else {
    error.value = result.error
  }

  isLoading.value = false
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-surface px-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4">
          <span class="text-white font-bold text-2xl">H</span>
        </div>
        <h1 class="text-2xl font-bold">Hotel Management System</h1>
        <p class="text-secondary mt-2">Sign in to your account</p>
      </div>

      <!-- Login form -->
      <div class="card">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Error message -->
          <div v-if="error" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm">
            {{ error }}
          </div>

          <!-- Email -->
          <div>
            <label for="email" class="label">Email address</label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              autocomplete="email"
              class="input"
              placeholder="admin@hotel.com"
            />
          </div>

          <!-- Password -->
          <div>
            <label for="password" class="label">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              autocomplete="current-password"
              class="input"
              placeholder="Enter your password"
            />
          </div>

          <!-- Remember me -->
          <div class="flex items-center justify-between">
            <label class="flex items-center">
              <input type="checkbox" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
              <span class="ml-2 text-sm">Remember me</span>
            </label>
            <a href="#" class="text-sm text-primary-600 hover:text-primary-500">Forgot password?</a>
          </div>

          <!-- Submit button -->
          <button
            type="submit"
            :disabled="isLoading"
            class="btn btn-primary w-full"
          >
            <span v-if="isLoading">Signing in...</span>
            <span v-else>Sign in</span>
          </button>
        </form>
      </div>

      <!-- Footer -->
      <p class="text-center text-sm text-secondary mt-6">
        Hotel Management System v1.0.0
      </p>
    </div>
  </div>
</template>
