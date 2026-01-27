<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useGuestsStore } from '@/stores/guests'

const route = useRoute()
const guestsStore = useGuestsStore()

onMounted(() => {
  guestsStore.fetchGuest(route.params.id)
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">Guest Details</h1>
    <div class="card" v-if="guestsStore.currentGuest">
      <p>{{ guestsStore.currentGuest.first_name }} {{ guestsStore.currentGuest.last_name }}</p>
    </div>
  </div>
</template>
