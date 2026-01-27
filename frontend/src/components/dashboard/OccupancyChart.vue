<script setup>
const props = defineProps({
  data: Array,
  title: String,
  type: {
    type: String,
    default: 'occupancy'
  }
})
</script>

<template>
  <div class="card">
    <h2 class="text-lg font-semibold mb-4">{{ title }}</h2>
    <div class="h-64 flex items-center justify-center text-secondary">
      <p>Chart visualization (requires Chart.js integration)</p>
    </div>
  </div>
</template>
