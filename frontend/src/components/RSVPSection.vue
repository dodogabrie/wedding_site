<template>
  <section class="relative min-h-screen py-20 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <h2 ref="header" class="font-script text-forest text-4xl md:text-5xl lg:text-6xl text-center mb-8 opacity-0">
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
          <div v-if="!selectedItem" key="bubbles">
            <!-- Search Bar -->
            <div class="mb-8">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Cerca per nome..."
                class="w-full max-w-md mx-auto block bg-cream text-forest font-serif px-6 py-3 border-2 border-forest/20 rounded-full focus:outline-none focus:border-forest/40 transition-colors"
              />
            </div>

            <!-- Heart Container -->
            <div ref="heartContainer" class="relative w-full aspect-square max-w-2xl mx-auto">
              <!-- Visible SVG path for reference -->
              <svg class="absolute inset-0 w-full h-full" viewBox="-10 -10 20 20" xmlns="http://www.w3.org/2000/svg">
                <path
                  id="heart-path"
                  :d="heartPathData"
                  fill="none"
                  stroke="red"
                  stroke-width="0.3"
                />
              </svg>

              <!-- Bubbles -->
              <button
                v-for="bubble in filteredBubbles"
                :key="bubble.id"
                :ref="el => setBubbleRef(el, bubble.id)"
                :data-bubble-id="bubble.id"
                @click="selectBubble(bubble)"
                :aria-label="bubble.fullName"
                class="rsvp-bubble absolute bg-cream text-forest font-serif px-4 py-2 rounded-full shadow-md transition-all duration-300 hover:shadow-lg hover:scale-110"
                style="will-change: transform"
              >
                {{ bubble.displayText }}
              </button>
            </div>
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
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { MotionPathPlugin } from 'gsap/MotionPathPlugin'

import RSVPCard from './RSVPCard.vue'
import RSVPFamilyCard from './RSVPFamilyCard.vue'
import { getFamilies, getGuests } from '../services/api'

gsap.registerPlugin(ScrollTrigger, MotionPathPlugin)
gsap.config({ force3D: true })

// Template refs used for section entrance animation and rotating bubbles layout.
const header = ref(null)
const heartContainer = ref(null)
const bubbleRefs = ref({})

// Data source collections and UI states.
const families = ref([])
const individuals = ref([])
const loading = ref(true)
const error = ref(null)

// Detail panel state.
const selectedItem = ref(null)
const selectedType = ref(null)
const searchQuery = ref('')

// Single GSAP timeline driving initial placement + infinite rotation.
const rotationTimeline = ref(null)

// Animation/layout constants for the rotating ring.
const ROTATION_DURATION = 60
const CIRCLE_RADIUS = 8
const PATH_SAMPLES = 200

const allBubbles = computed(() => {
  const bubbles = []

  families.value.forEach(family => {
    bubbles.push({
      id: `f-${family.id}`,
      type: 'family',
      displayText: family.family_name,
      fullName: family.family_name,
      data: family
    })
  })

  individuals.value.forEach(guest => {
    bubbles.push({
      id: `i-${guest.id}`,
      type: 'individual',
      displayText: guest.name,
      fullName: guest.name,
      data: guest
    })
  })

  return bubbles
})

const filteredBubbles = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  const hasQuery = query.length > 0

  // Keep original order, adding search metadata used by highlight animation.
  return allBubbles.value.map(bubble => ({
    ...bubble,
    matches: hasQuery && bubble.fullName.toLowerCase().startsWith(query),
    hasQuery
  }))
})

const heartPathData = computed(() => {
  const points = []

  // Build a sampled circular SVG path used as the motion path for each bubble.
  for (let i = 0; i < PATH_SAMPLES; i++) {
    const t = (i / PATH_SAMPLES) * 2 * Math.PI
    const x = CIRCLE_RADIUS * Math.cos(t)
    const y = CIRCLE_RADIUS * Math.sin(t)
    points.push([x, y])
  }

  const pathParts = points.map((point, i) =>
    i === 0 ? `M ${point[0]} ${point[1]}` : `L ${point[0]} ${point[1]}`
  )

  return pathParts.join(' ') + ' Z'
})

function setBubbleRef(el, id) {
  if (el) {
    bubbleRefs.value[id] = el
  } else {
    delete bubbleRefs.value[id]
  }
}

/**
 * Fetch RSVP entities once at mount and set loading/error states.
 */
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

/**
 * Resolve one rendered bubble element by stable bubble id.
 */
function getBubbleElement(bubbleId, bubbleElements) {
  return Array.from(bubbleElements).find(el => el.dataset.bubbleId === bubbleId)
}

/**
 * Open the chosen bubble.
 * Individuals animate to center before switching to detail view.
 */
function selectBubble(bubble) {
  if (bubble.type === 'individual') {
    const element = bubbleRefs.value[bubble.id]
    if (!element) return

    if (rotationTimeline.value) {
      rotationTimeline.value.pause()
    }

    gsap.to(element, {
      x: 0,
      y: 0,
      left: '50%',
      top: '50%',
      scale: 1.5,
      backgroundColor: '#9DAD8F',
      duration: 0.5,
      ease: 'back.out(1.7)'
    })

    setTimeout(() => {
      selectedItem.value = bubble.data
      selectedType.value = bubble.type
    }, 500)
  } else {
    if (rotationTimeline.value) {
      rotationTimeline.value.pause()
    }

    selectedItem.value = bubble.data
    selectedType.value = bubble.type
  }
}

function clearSelection() {
  selectedItem.value = null
  selectedType.value = null
  searchQuery.value = ''
}

/**
 * Recreate bubble animation when transition returns to the bubbles view.
 */
function onTransitionEnter(_el) {
  if (!selectedItem.value) {
    if (rotationTimeline.value) {
      rotationTimeline.value.kill()
      rotationTimeline.value = null
    }

    nextTick(() => {
      setTimeout(() => {
        initializeRotation()
        setTimeout(() => updateBubblePositions(), 50)
      }, 100)
    })
  }
}

/**
 * Keep local individuals collection in sync after card edits.
 */
function updateIndividual(updated) {
  const index = individuals.value.findIndex(g => g.id === updated.id)
  if (index !== -1) {
    individuals.value[index] = updated
    if (selectedType.value === 'individual' && selectedItem.value?.id === updated.id) {
      selectedItem.value = updated
    }
  }
}

/**
 * Keep family guest entry in sync after child component emits updates.
 */
function updateFamilyGuest({ guestId, guest }) {
  for (const family of families.value) {
    const guestIndex = family.guests.findIndex(g => g.id === guestId)
    if (guestIndex !== -1) {
      family.guests[guestIndex] = guest
      break
    }
  }
}

/**
 * Build one timeline:
 * 1) snap each bubble to a unique starting progress on the path
 * 2) rotate forever with synchronized speed.
 */
function initializeRotation() {
  if (rotationTimeline.value) {
    return
  }

  const bubbles = allBubbles.value
  if (bubbles.length === 0) return

  const svgPath = document.querySelector('#heart-path')
  if (!svgPath) {
    console.error('Heart path not found')
    return
  }

  const bubbleElements = heartContainer.value?.querySelectorAll('.rsvp-bubble')
  if (!bubbleElements || bubbleElements.length === 0) {
    console.error('No bubble elements found in DOM')
    return
  }

  const masterTimeline = gsap.timeline()

  Array.from(bubbleElements).forEach((element, index) => {
    const startProgress = index / bubbleElements.length

    masterTimeline.to(element, {
      motionPath: {
        path: svgPath,
        align: svgPath,
        alignOrigin: [0.5, 0.5],
        start: startProgress,
        end: startProgress
      },
      duration: 1,
      ease: 'power2.out'
    }, 0)
  })

  const rotationStart = masterTimeline.duration()

  Array.from(bubbleElements).forEach((element, index) => {
    const startProgress = index / bubbleElements.length
    const endProgress = startProgress + 1

    masterTimeline.to(element, {
      motionPath: {
        path: svgPath,
        align: svgPath,
        alignOrigin: [0.5, 0.5],
        start: startProgress,
        end: endProgress
      },
      duration: ROTATION_DURATION,
      ease: 'none',
      repeat: -1,
      repeatDelay: 0
    }, rotationStart)
  })

  rotationTimeline.value = masterTimeline
}

/**
 * Apply search emphasis:
 * - matching bubbles move up and scale
 * - non-matching bubbles return to baseline style.
 */
function updateBubblePositions() {
  if (!rotationTimeline.value) {
    console.warn('Rotation timeline not initialized yet')
    return
  }

  const bubbles = filteredBubbles.value
  const hasQuery = bubbles.some(b => b.hasQuery)

  const bubbleElements = heartContainer.value?.querySelectorAll('.rsvp-bubble')
  if (!bubbleElements) return

  if (!hasQuery) {
    bubbleElements.forEach(element => {
      gsap.to(element, {
        yPercent: 0,
        scale: 1,
        backgroundColor: '#F5F2EB',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        duration: 0.3,
        ease: 'power2.out'
      })
    })
    return
  }

  bubbles.forEach((bubble) => {
    const element = getBubbleElement(bubble.id, bubbleElements)

    if (!element) return

    if (bubble.matches) {
      gsap.to(element, {
        yPercent: -180,
        scale: 1.3,
        backgroundColor: '#9DAD8F',
        boxShadow: '0 20px 25px -5px rgba(61, 79, 61, 0.3), 0 10px 10px -5px rgba(61, 79, 61, 0.2)',
        duration: 0.25,
        ease: 'back.out(2)'
      })
    } else {
      gsap.to(element, {
        yPercent: 0,
        scale: 1,
        backgroundColor: '#F5F2EB',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        duration: 0.3,
        ease: 'power2.out'
      })
    }
  })
}

watch(searchQuery, () => {
  if (!loading.value && !selectedItem.value && rotationTimeline.value) {
    updateBubblePositions()
  }
})

onMounted(async () => {
  await fetchData()
  await nextTick()

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

  await nextTick()

  const initWithRetry = () => {
    const svgPath = document.querySelector('#heart-path')
    if (svgPath) {
      initializeRotation()
      setTimeout(() => updateBubblePositions(), 50)
    } else {
      setTimeout(initWithRetry, 100)
    }
  }

  setTimeout(initWithRetry, 200)
})

onBeforeUnmount(() => {
  if (rotationTimeline.value) {
    rotationTimeline.value.kill()
    rotationTimeline.value = null
  }
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

@media (prefers-reduced-motion: reduce) {
  .rsvp-bubble {
    animation: none !important;
  }
}
</style>
