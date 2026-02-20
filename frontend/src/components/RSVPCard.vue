<template>
  <div
    class="card-individual flex items-center justify-between gap-4 transition-all hover:shadow-lg"
    :class="guest.attending === true ? 'bg-[#eef5e6] ring-2 ring-forest/45 shadow-[0_0_0_3px_rgba(61,79,61,0.24),0_0_34px_rgba(157,173,143,0.62)]' : ''"
  >
    <span class="font-serif text-forest text-lg">{{ guest.name }}</span>
    <label class="relative flex items-center cursor-pointer">
      <input
        type="checkbox"
        :checked="guest.attending"
        @change="toggleAttending"
        class="sr-only peer"
        :disabled="loading"
      />
      <div
        class="w-6 h-6 border-2 border-forest rounded transition-colors peer-checked:bg-forest peer-checked:border-forest flex items-center justify-center"
        :class="{ 'opacity-50': loading }"
      >
        <svg
          v-if="guest.attending"
          class="w-4 h-4 text-cream"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
        </svg>
      </div>
    </label>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { updateGuest } from '../services/api'

const props = defineProps({
  guest: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['updated'])

const loading = ref(false)

async function toggleAttending() {
  loading.value = true
  try {
    const newStatus = !props.guest.attending
    const updated = await updateGuest(props.guest.id, { attending: newStatus })
    emit('updated', updated)
  } catch (error) {
    console.error('Failed to update RSVP:', error)
  } finally {
    loading.value = false
  }
}
</script>
