<template>
  <div class="card transition-all hover:shadow-lg">
    <h3 class="font-serif text-forest text-lg font-medium mb-3">
      {{ family.family_name }}
    </h3>
    <ul class="space-y-2">
      <li
        v-for="guest in family.guests"
        :key="guest.id"
        class="flex items-center justify-between gap-4"
      >
        <span class="font-serif text-forest flex items-center gap-2">
          <span class="text-forest/60">*</span>
          {{ guest.name }}
        </span>
        <label class="relative flex items-center cursor-pointer">
          <input
            type="checkbox"
            :checked="guest.attending"
            @change="toggleGuestAttending(guest)"
            class="sr-only peer"
            :disabled="loading"
          />
          <div
            class="w-5 h-5 border-2 border-forest rounded transition-colors peer-checked:bg-forest peer-checked:border-forest flex items-center justify-center"
            :class="{ 'opacity-50': loading }"
          >
            <svg
              v-if="guest.attending"
              class="w-3 h-3 text-cream"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </label>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { updateGuest } from '../services/api'

const props = defineProps({
  family: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['updated'])

const loading = ref(false)

async function toggleGuestAttending(guest) {
  loading.value = true
  try {
    const newStatus = !guest.attending
    const updated = await updateGuest(guest.id, { attending: newStatus })
    emit('updated', { guestId: guest.id, guest: updated })
  } catch (error) {
    console.error('Failed to update RSVP:', error)
  } finally {
    loading.value = false
  }
}
</script>
