<template>
  <div class="card transition-all hover:shadow-lg">
    <h3 v-if="showTitle" class="font-serif text-forest text-lg font-medium mb-3">
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
        <div class="flex items-center gap-2">
          <button
            type="button"
            class="font-serif px-3 py-1.5 rounded-full border-2 transition-colors text-sm"
            :class="guest.attending === true ? 'bg-forest text-cream border-forest' : 'bg-forest/14 text-forest border-forest/55 hover:bg-forest/20 hover:border-forest/70'"
            :disabled="loadingGuestId === guest.id"
            aria-label="Ci sarò"
            @click="setGuestAttending(guest, true)"
          >
            <span class="md:hidden">✓</span>
            <span class="hidden md:inline">✓ Ci sarò</span>
          </button>
          <button
            type="button"
            class="font-serif px-3 py-1.5 rounded-full border-2 transition-colors text-sm"
            :class="guest.attending === false ? 'bg-forest text-cream border-forest' : 'bg-forest/14 text-forest border-forest/55 hover:bg-forest/20 hover:border-forest/70'"
            :disabled="loadingGuestId === guest.id"
            aria-label="Non ci sarò"
            @click="setGuestAttending(guest, false)"
          >
            <span class="md:hidden">✕</span>
            <span class="hidden md:inline">✕ Non ci sarò</span>
          </button>
        </div>
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
  },
  showTitle: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['updated'])

const loadingGuestId = ref(null)

async function setGuestAttending(guest, attending) {
  if (loadingGuestId.value !== null) return
  if (guest.attending === attending) return

  loadingGuestId.value = guest.id
  try {
    const updated = await updateGuest(guest.id, { attending })
    if (!sessionStorage.getItem('rsvp_updated')) sessionStorage.setItem('rsvp_updated', 'pending')
    emit('updated', { guestId: guest.id, guest: updated })
  } catch (error) {
    console.error('Failed to update RSVP:', error)
  } finally {
    loadingGuestId.value = null
  }
}
</script>
