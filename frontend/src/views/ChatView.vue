<script setup>
import { ref } from 'vue'

const activeTab = ref('whatsapp')
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold">Chat</h1>
      <p class="text-secondary">WhatsApp conversations and AI assistant</p>
    </div>

    <div class="flex space-x-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1 w-fit">
      <button
        @click="activeTab = 'whatsapp'"
        :class="['px-4 py-2 text-sm font-medium rounded-md transition-colors', activeTab === 'whatsapp' ? 'bg-white dark:bg-gray-700 shadow' : '']"
      >
        WhatsApp
      </button>
      <button
        @click="activeTab = 'ai'"
        :class="['px-4 py-2 text-sm font-medium rounded-md transition-colors', activeTab === 'ai' ? 'bg-white dark:bg-gray-700 shadow' : '']"
      >
        AI Assistant
      </button>
    </div>

    <div class="card min-h-[500px] flex items-center justify-center text-secondary">
      <p v-if="activeTab === 'whatsapp'">WhatsApp conversations will appear here</p>
      <p v-else>AI Assistant chat will appear here</p>
    </div>
  </div>
</template>
