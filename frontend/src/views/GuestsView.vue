<script setup>
import { onMounted } from 'vue'
import { useGuestsStore } from '@/stores/guests'

const guestsStore = useGuestsStore()

onMounted(() => {
  guestsStore.fetchGuests()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Guests</h1>
        <p class="text-secondary">Guest CRM and profiles</p>
      </div>
      <button class="btn btn-primary">Add Guest</button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="guest in guestsStore.guests" :key="guest.id" class="card">
        <div class="flex items-start space-x-4">
          <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
            <span class="text-primary-600 dark:text-primary-400 font-semibold text-lg">
              {{ guest.first_name?.charAt(0) }}{{ guest.last_name?.charAt(0) }}
            </span>
          </div>
          <div class="flex-1">
            <div class="flex items-center space-x-2">
              <h3 class="font-semibold">{{ guest.first_name }} {{ guest.last_name }}</h3>
              <span v-if="guest.is_vip" class="badge badge-warning">VIP</span>
            </div>
            <p class="text-sm text-secondary">{{ guest.email }}</p>
            <p class="text-sm text-secondary">{{ guest.phone }}</p>
            <div class="mt-2 text-sm">
              <span class="text-secondary">{{ guest.total_stays }} stays</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
