<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-surface">
    <div class="text-center">
      <h1 class="text-6xl font-bold text-primary-600">404</h1>
      <p class="text-xl mt-4">Page not found</p>
      <p class="text-secondary mt-2">The page you're looking for doesn't exist.</p>
      <button @click="router.push('/')" class="btn btn-primary mt-6">Go to Dashboard</button>
    </div>
  </div>
</template>
