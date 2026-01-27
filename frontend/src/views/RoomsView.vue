<script setup>
import { onMounted } from 'vue'
import { useRoomsStore } from '@/stores/rooms'

const roomsStore = useRoomsStore()

onMounted(() => {
  roomsStore.fetchRooms()
  roomsStore.fetchRoomTypes()
})

const getStatusColor = (status) => {
  const colors = {
    available: 'bg-green-500',
    booked: 'bg-blue-500',
    checked_in: 'bg-yellow-500',
    maintenance: 'bg-red-500',
    cleaning: 'bg-orange-500'
  }
  return colors[status] || 'bg-gray-500'
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Rooms</h1>
        <p class="text-secondary">Manage hotel rooms and availability</p>
      </div>
      <button class="btn btn-primary">Add Room</button>
    </div>

    <!-- Room status summary -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <div v-for="(count, status) in roomsStore.roomsByStatus" :key="status" class="card text-center">
        <div class="flex items-center justify-center space-x-2">
          <span :class="['w-3 h-3 rounded-full', getStatusColor(status)]"></span>
          <span class="capitalize">{{ status.replace('_', ' ') }}</span>
        </div>
        <p class="text-2xl font-bold mt-2">{{ count }}</p>
      </div>
    </div>

    <!-- Rooms grid by floor -->
    <div v-for="(rooms, floor) in roomsStore.roomsByFloor" :key="floor" class="card">
      <h3 class="text-lg font-semibold mb-4">Floor {{ floor }}</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div
          v-for="room in rooms"
          :key="room.id"
          class="p-4 rounded-lg border-2 cursor-pointer hover:shadow-md transition-shadow"
          :class="{
            'border-green-500 bg-green-50 dark:bg-green-900/20': room.status === 'available',
            'border-blue-500 bg-blue-50 dark:bg-blue-900/20': room.status === 'booked',
            'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20': room.status === 'checked_in',
            'border-red-500 bg-red-50 dark:bg-red-900/20': room.status === 'maintenance',
            'border-orange-500 bg-orange-50 dark:bg-orange-900/20': room.status === 'cleaning'
          }"
        >
          <p class="font-bold text-lg">{{ room.room_number }}</p>
          <p class="text-sm text-secondary">{{ room.room_type?.name }}</p>
          <span class="text-xs capitalize">{{ room.status.replace('_', ' ') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
