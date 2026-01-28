<template>
  <section class="relative min-h-screen py-20 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <h2 ref="header" class="font-script text-forest text-4xl md:text-5xl lg:text-6xl text-center mb-12 opacity-0">
        Sarai presente?
      </h2>

      <!-- Loading state -->
      <div v-if="loading" class="text-center text-forest">
        <p class="font-serif text-lg">Caricamento...</p>
      </div>

      <!-- Error state -->
      <div v-else-if="error" class="text-center text-red-800">
        <p class="font-serif text-lg">{{ error }}</p>
      </div>

      <!-- Content -->
      <div v-else>
        <Transition name="fade" mode="out-in" @enter="onTransitionEnter">
          <!-- Bubbles View -->
          <div v-if="!selectedItem" key="bubbles" ref="bubblesContainer" class="flex flex-wrap justify-center gap-4">
            <!-- Family Bubbles -->
            <button
              v-for="family in families"
              :key="'f-' + family.id"
              @click="selectFamily(family)"
              class="rsvp-bubble opacity-0 bg-cream text-forest font-serif px-6 py-3 rounded-full shadow-md hover:shadow-lg hover:scale-105 transition-all duration-300"
            >
              {{ family.family_name }}
            </button>
            
            <!-- Individual Bubbles -->
            <button
              v-for="guest in individuals"
              :key="'i-' + guest.id"
              @click="selectIndividual(guest)"
              class="rsvp-bubble opacity-0 bg-cream text-forest font-serif px-6 py-3 rounded-full shadow-md hover:shadow-lg hover:scale-105 transition-all duration-300"
            >
              {{ guest.name }}
            </button>
          </div>

          <!-- Detail View -->
          <div v-else key="detail" class="max-w-xl mx-auto">
            <button 
              @click="clearSelection"
              class="mb-6 flex items-center text-forest hover:text-forest/80 transition-colors font-serif"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Torna alla lista
            </button>

            <RSVPFamilyCard
              v-if="selectedType === 'family'"
              :family="selectedItem"
              @updated="updateFamilyGuest"
              class="w-full"
            />

            <RSVPCard
              v-if="selectedType === 'individual'"
              :guest="selectedItem"
              @updated="updateIndividual"
              class="w-full"
            />
          </div>
        </Transition>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

import cornerSvg from '../assets/corner.svg'
import RSVPCard from './RSVPCard.vue'
import RSVPFamilyCard from './RSVPFamilyCard.vue'
import { getFamilies, getGuests } from '../services/api'

gsap.registerPlugin(ScrollTrigger)

const header = ref(null)
const bubblesContainer = ref(null)

const families = ref([])
const individuals = ref([])
const loading = ref(true)
const error = ref(null)

const selectedItem = ref(null)
const selectedType = ref(null) // 'family' | 'individual'

async function fetchData() {
  try {
    const [familiesData, guestsData] = await Promise.all([
      getFamilies(),
      getGuests()
    ])
    families.value = familiesData
    individuals.value = guestsData
  } catch (e) {
    error.value = 'Errore nel caricamento dei dati'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function selectFamily(family) {
  selectedItem.value = family
  selectedType.value = 'family'
}

function selectIndividual(guest) {
  selectedItem.value = guest
  selectedType.value = 'individual'
}

function clearSelection() {
  selectedItem.value = null
  selectedType.value = null
}

function onTransitionEnter(el) {
  // If we are entering the bubbles view (no selected item), animate them
  if (!selectedItem.value) {
    animateBubbles(true, el)
  }
}

function updateIndividual(updated) {
  const index = individuals.value.findIndex(g => g.id === updated.id)
  if (index !== -1) {
    individuals.value[index] = updated
    // Update selected item if it's the one currently viewed
    if (selectedType.value === 'individual' && selectedItem.value?.id === updated.id) {
      selectedItem.value = updated
    }
  }
}

function updateFamilyGuest({ guestId, guest }) {
  for (const family of families.value) {
    const guestIndex = family.guests.findIndex(g => g.id === guestId)
    if (guestIndex !== -1) {
      family.guests[guestIndex] = guest
      // Update selected item if it's the one currently viewed
      if (selectedType.value === 'family' && selectedItem.value?.id === family.id) {
         // Create a new reference to trigger reactivity if needed, 
         // though nested object mutation usually works in Vue 3 
         // if the specific property is reactive. 
         // Here we are mutating the array inside the family object.
      }
      break
    }
  }
}

function animateBubbles(immediate = false, container = null) {
  const targetContainer = container || bubblesContainer.value
  const bubbles = targetContainer?.querySelectorAll('.rsvp-bubble')
  if (bubbles && bubbles.length) {
    // Kill any existing tweens on these elements to prevent conflicts
    gsap.killTweensOf(bubbles)

    const fromVars = {
      opacity: 0,
      y: 20,
      scale: 0.9
    }

    const toVars = {
      opacity: 1,
      y: 0,
      scale: 1,
      duration: 0.5,
      stagger: 0.05,
      ease: 'back.out(1.2)'
    }

    if (!immediate) {
      toVars.scrollTrigger = {
        trigger: targetContainer,
        start: 'top 85%',
        toggleActions: 'play none none reverse'
      }
    }

    gsap.fromTo(bubbles, fromVars, toVars)
  }
}

onMounted(async () => {
  await fetchData()
  await nextTick()

  // Animate header
  gsap.to(header.value, {
    opacity: 1,
    y: 0,
    duration: 0.8,
    scrollTrigger: {
      trigger: header.value,
      start: 'top 80%',
      toggleActions: 'play none none reverse'
    }
  })

  animateBubbles(false)
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
