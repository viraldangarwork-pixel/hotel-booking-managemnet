<script setup>
import { ref } from 'vue'

const props = defineProps({
  checkIns: Array,
  checkOuts: Array
})

const activeTab = ref('check-ins')
</script>

<template>
  <div class="card">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold">Today's Schedule</h2>
      <div class="flex space-x-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
        <button
          @click="activeTab = 'check-ins'"
          :class="[
            'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
            activeTab === 'check-ins'
              ? 'bg-white dark:bg-gray-700 shadow'
              : 'hover:bg-gray-200 dark:hover:bg-gray-700'
          ]"
        >
          Check-ins ({{ checkIns?.length || 0 }})
        </button>
        <button
          @click="activeTab = 'check-outs'"
          :class="[
            'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
            activeTab === 'check-outs'
              ? 'bg-white dark:bg-gray-700 shadow'
              : 'hover:bg-gray-200 dark:hover:bg-gray-700'
          ]"
        >
          Check-outs ({{ checkOuts?.length || 0 }})
        </button>
      </div>
    </div>

    <div class="space-y-3">
      <template v-if="activeTab === 'check-ins'">
        <div v-if="!checkIns?.length" class="text-center py-8 text-secondary">
          No check-ins scheduled for today
        </div>
        <div
          v-for="booking in checkIns"
          :key="booking.id"
          class="flex items-center justify-between p-3 bg-surface rounded-lg"
        >
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
              <span class="text-primary-600 dark:text-primary-400 font-semibold">
                {{ booking.guest_name?.charAt(0) || 'G' }}
              </span>
            </div>
            <div>
              <p class="font-medium flex items-center">
                {{ booking.guest_name }}
                <span v-if="booking.is_vip" class="ml-2 badge badge-warning">VIP</span>
              </p>
              <p class="text-sm text-secondary">Room {{ booking.room_number }} • {{ booking.booking_ref }}</p>
            </div>
          </div>
          <button class="btn btn-primary btn-sm">Check In</button>
        </div>
      </template>

      <template v-else>
        <div v-if="!checkOuts?.length" class="text-center py-8 text-secondary">
          No check-outs scheduled for today
        </div>
        <div
          v-for="booking in checkOuts"
          :key="booking.id"
          class="flex items-center justify-between p-3 bg-surface rounded-lg"
        >
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-orange-100 dark:bg-orange-900/30 rounded-full flex items-center justify-center">
              <span class="text-orange-600 dark:text-orange-400 font-semibold">
                {{ booking.guest_name?.charAt(0) || 'G' }}
              </span>
            </div>
            <div>
              <p class="font-medium">{{ booking.guest_name }}</p>
              <p class="text-sm text-secondary">Room {{ booking.room_number }} • {{ booking.booking_ref }}</p>
            </div>
          </div>
          <button class="btn btn-secondary btn-sm">Check Out</button>
        </div>
      </template>
    </div>
  </div>
</template>
