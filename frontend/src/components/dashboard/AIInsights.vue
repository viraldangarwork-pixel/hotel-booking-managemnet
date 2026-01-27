<script setup>
const props = defineProps({
  insights: Array
})

const getTypeStyles = (type) => {
  const styles = {
    warning: 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800',
    alert: 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800',
    suggestion: 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800'
  }
  return styles[type] || styles.suggestion
}

const getIconColor = (type) => {
  const colors = {
    warning: 'text-yellow-600',
    alert: 'text-red-600',
    suggestion: 'text-blue-600'
  }
  return colors[type] || colors.suggestion
}
</script>

<template>
  <div class="card">
    <div class="flex items-center space-x-2 mb-4">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
      <h2 class="text-lg font-semibold">AI Insights</h2>
    </div>

    <div v-if="!insights?.length" class="text-center py-8 text-secondary">
      No insights available
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="(insight, index) in insights"
        :key="index"
        :class="['p-3 rounded-lg border', getTypeStyles(insight.type)]"
      >
        <div class="flex items-start space-x-3">
          <svg :class="['h-5 w-5 mt-0.5 flex-shrink-0', getIconColor(insight.type)]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path v-if="insight.type === 'alert'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            <path v-else-if="insight.type === 'warning'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <div>
            <p class="font-medium text-sm">{{ insight.title }}</p>
            <p class="text-sm text-secondary mt-1">{{ insight.message }}</p>
            <button v-if="insight.action" class="text-sm text-primary-600 hover:underline mt-2">
              {{ insight.action }} →
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
