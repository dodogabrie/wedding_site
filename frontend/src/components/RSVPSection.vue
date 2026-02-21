<template>
  <section class="relative min-h-screen py-20 px-4">
    <!-- Flight overlay for animated clones -->
    <div ref="flightOverlay" class="fixed inset-0 pointer-events-none" style="z-index: 50;"></div>

    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <h2 ref="header" class="font-script block overflow-visible text-forest text-4xl md:text-5xl lg:text-6xl leading-[1.35] pt-3 pb-1 text-center mb-8 opacity-0">
        <span class="script-glyph-safe">Sarai presente?</span>
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
        <div class="mb-8">
          <div class="w-full max-w-md mx-auto">
            <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-forest/50 pointer-events-none">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-4.35-4.35m1.85-5.15a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z" />
                  </svg>
                </span>
                <input
                  id="rsvp-search"
                  ref="searchInput"
                  v-model="searchQuery"
                  type="text"
                  name="rsvp-search-no-history"
                  autocomplete="off"
                  autocorrect="off"
                  autocapitalize="none"
                  spellcheck="false"
                  :placeholder="isMobile ? 'Cerca il tuo nome' : 'Clicca per cercare il tuo nome'"
                  class="w-full block bg-transparent text-forest font-serif leading-[1.35] pl-11 pr-12 py-3 border-2 border-forest/55 rounded-2xl placeholder:text-forest/55 shadow-[0_0_0_1px_rgba(61,79,61,0.20),0_10px_26px_rgba(20,35,20,0.14)] focus:outline-none focus:border-forest/80 focus:shadow-[0_0_0_2px_rgba(61,79,61,0.26),0_12px_30px_rgba(20,35,20,0.18)] transition-colors"
                />
                <button
                  v-if="searchQuery.trim().length > 0"
                  type="button"
                  aria-label="Cancella ricerca"
                  class="absolute right-3 top-1/2 -translate-y-1/2 inline-flex items-center justify-center w-7 h-7 rounded-full border-2 border-forest/40 bg-transparent text-forest/70 hover:text-forest hover:border-forest/60 hover:bg-forest/10 transition-colors"
                  @click="clearSearch"
                >
                  <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M6 6l12 12M18 6 6 18" />
                  </svg>
                </button>
            </div>
          </div>
          <!-- Reserve chip area height to avoid pushing rings down when matches appear -->
          <div class="mt-3 mx-auto max-w-md h-16 relative">
            <div
              v-if="searchQuery.trim().length > 0 && matchingBubbles.length > 0 && !showSingleGuestActions && !showFamilyDetailExactMatch"
              class="absolute inset-0 flex flex-wrap gap-2 justify-center content-start"
            >
              <button
                v-for="bubble in matchingBubbles"
                :key="`match-${bubble.id}`"
                :ref="el => setChipRef(el, bubble.id)"
                @click="selectBubble(bubble)"
                class="bg-cream/95 text-forest font-serif text-sm px-3 py-1 rounded-full border border-forest/20 shadow-sm"
                :class="{
                  'single-match-pulse': singleMatchedGuestBubble && bubble.id === singleMatchedGuestBubble.id && !showSingleGuestActions
                }"
                :style="{ opacity: dockedBubbleIds[bubble.id] ? 1 : 0 }"
              >
                <span>{{ bubble.displayText }}</span>
              </button>
            </div>
            <div
              v-if="showSingleGuestActions && singleMatchedGuestBubble"
              class="absolute left-1/2 -translate-x-1/2 top-0 mt-1 w-full max-w-md z-20 pointer-events-none"
            >
              <div class="pointer-events-auto flex items-center justify-center gap-3">
                <button
                  class="font-serif px-5 py-2 rounded-full border-2 transition-colors backdrop-blur-[1px]"
                  :class="singleMatchedGuestBubble.data.attending === true ? 'bg-forest text-cream border-forest shadow-[0_0_0_2px_rgba(61,79,61,0.26),0_12px_30px_rgba(20,35,20,0.18)]' : 'bg-forest/14 text-forest border-forest/55 hover:bg-forest/20 hover:border-forest/70 shadow-[0_0_0_1px_rgba(61,79,61,0.20),0_10px_26px_rgba(20,35,20,0.14)]'"
                  :disabled="inlineGuestLoading"
                  @click="setSingleGuestAttendance(singleMatchedGuestBubble, true)"
                >
                  ✓ Ci sarò
                </button>
                <button
                  class="font-serif px-5 py-2 rounded-full border-2 transition-colors backdrop-blur-[1px]"
                  :class="singleMatchedGuestBubble.data.attending === false ? 'bg-forest text-cream border-forest shadow-[0_0_0_2px_rgba(61,79,61,0.26),0_12px_30px_rgba(20,35,20,0.18)]' : 'bg-forest/14 text-forest border-forest/55 hover:bg-forest/20 hover:border-forest/70 shadow-[0_0_0_1px_rgba(61,79,61,0.20),0_10px_26px_rgba(20,35,20,0.14)]'"
                  :disabled="inlineGuestLoading"
                  @click="setSingleGuestAttendance(singleMatchedGuestBubble, false)"
                >
                  ✕ Non ci sarò
                </button>
              </div>
              <p v-if="inlineGuestError" class="mt-2 text-center text-sm text-red-800 font-serif">
                {{ inlineGuestError }}
              </p>
            </div>
          </div>
        </div>

        <div class="relative">
          <!-- Detail View -->
          <Transition name="fade">
            <div v-if="selectedItem" class="absolute left-1/2 -translate-x-1/2 top-0 w-full max-w-xl px-4 md:px-0 z-20">
              <RSVPFamilyCard
                v-if="selectedType === 'family'"
                :family="selectedItem"
                :show-title="!showFamilyDetailExactMatch"
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

          <div
            :class="selectedItem ? 'pointer-events-none opacity-45 transition-opacity duration-300' : 'transition-opacity duration-300'"
          >
            <!-- Two clipped side tracks on both desktop and mobile. -->
            <div
              ref="ringsContainer"
              class="relative w-[100dvw] max-w-[100dvw] left-1/2 -translate-x-1/2 h-[68vh] min-h-[28rem] md:h-[36rem] overflow-visible"
            >
            <div class="absolute left-0 top-0 bottom-0 w-1/2 overflow-visible pointer-events-none pl-2 md:pl-0" style="clip-path: inset(-200% 0% -200% -200%)">
              <div
                ref="leftTrackContainer"
                class="absolute inset-0 pointer-events-auto"
              >
                <svg class="absolute inset-0 w-full h-full" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                  <path
                    ref="leftPath"
                    :d="leftTrajectoryPathData"
                    fill="none"
                    :stroke="SHOW_TRAJECTORY_DEBUG ? 'red' : 'transparent'"
                    :stroke-width="SHOW_TRAJECTORY_DEBUG ? 0.35 : 0"
                  />
                </svg>

                <button
                  v-for="bubble in leftTrackBubbles"
                  :key="bubble.id"
                  :ref="el => setBubbleRef(el, bubble.id)"
                  :data-bubble-id="bubble.id"
                  data-track="left"
                  @click="selectBubble(bubble)"
                  :aria-label="bubble.fullName"
                  class="rsvp-bubble absolute overflow-visible"
                  style="will-change: transform"
                >
                  <span
                    class="bubble-visual block overflow-visible bg-cream text-forest font-serif text-[0.96rem] md:text-[1.2rem] leading-[1.45] text-center whitespace-normal md:whitespace-nowrap max-w-[44vw] md:max-w-none px-4.5 md:px-4 py-[0.72rem] md:py-2.5 rounded-full border-2 border-transparent shadow-md transition-shadow duration-200 hover:shadow-lg"
                    :class="{ 'yes-border': bubble.attendanceState === 'yes' }"
                  >
                    {{ bubble.displayText }}
                  </span>
                </button>
              </div>
            </div>

            <div class="absolute right-0 top-0 bottom-0 w-1/2 overflow-visible pointer-events-none pr-2 md:pr-0" style="clip-path: inset(-200% -200% -200% 0%)">
              <div
                ref="rightTrackContainer"
                class="absolute inset-0 pointer-events-auto"
              >
                <svg class="absolute inset-0 w-full h-full" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                  <path
                    ref="rightPath"
                    :d="rightTrajectoryPathData"
                    fill="none"
                    :stroke="SHOW_TRAJECTORY_DEBUG ? 'red' : 'transparent'"
                    :stroke-width="SHOW_TRAJECTORY_DEBUG ? 0.35 : 0"
                  />
                </svg>

                <button
                  v-for="bubble in rightTrackBubbles"
                  :key="bubble.id"
                  :ref="el => setBubbleRef(el, bubble.id)"
                  :data-bubble-id="bubble.id"
                  data-track="right"
                  @click="selectBubble(bubble)"
                  :aria-label="bubble.fullName"
                  class="rsvp-bubble absolute overflow-visible"
                  style="will-change: transform"
                >
                  <span
                    class="bubble-visual block overflow-visible bg-cream text-forest font-serif text-[0.96rem] md:text-[1.2rem] leading-[1.45] text-center whitespace-normal md:whitespace-nowrap max-w-[44vw] md:max-w-none px-4.5 md:px-4 py-[0.72rem] md:py-2.5 rounded-full border-2 border-transparent shadow-md transition-shadow duration-200 hover:shadow-lg"
                    :class="{ 'yes-border': bubble.attendanceState === 'yes' }"
                  >
                    {{ bubble.displayText }}
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
        </div>
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
import { getFamilies, getGuests, updateGuest } from '../services/api'

gsap.registerPlugin(ScrollTrigger, MotionPathPlugin)
gsap.config({ force3D: true })

// Template refs used by entrance animation and rotating track layouts.
const header = ref(null)
const ringsContainer = ref(null)
const leftTrackContainer = ref(null)
const rightTrackContainer = ref(null)
const leftPath = ref(null)
const rightPath = ref(null)
const bubbleRefs = ref({})
const flightOverlay = ref(null)
const chipRefs = ref({})
const searchInput = ref(null)

// Data source collections and UI states.
const families = ref([])
const individuals = ref([])
const loading = ref(true)
const error = ref(null)

// Detail panel and responsiveness states.
const selectedItem = ref(null)
const selectedType = ref(null)
const searchQuery = ref('')
const isMobile = ref(false)

// Per-bubble rotation tweens and slot metadata.
const bubbleTweens = new Map()
const bubbleSlots = new Map()
let rotationGeneration = 0
let removeMediaListener = null

// Flight state: tracks bubbles currently in flight or docked at chip area.
const flyingBubbles = new Map()
const dockedBubbleIds = ref({})
let reconcileTimer = null
const staggerFlightTimers = new Set()
let reconcileGeneration = 0
const prefersReducedMotion = ref(false)
const inlineGuestLoading = ref(false)
const inlineGuestError = ref('')

// Animation/layout constants for side trajectories.
const ROTATION_DURATION = 60
const TRAJECTORY_RADIUS_X_DESKTOP = 80
const TRAJECTORY_RADIUS_Y_DESKTOP = 44
const TRAJECTORY_SIDE_OFFSET_DESKTOP = 36

const TRAJECTORY_RADIUS_X_MOBILE = 76
const TRAJECTORY_RADIUS_Y_MOBILE = 82
const TRAJECTORY_SIDE_OFFSET_MOBILE = 34
const TRAJECTORY_CENTER_Y_MOBILE = 4
const PATH_SAMPLES = 200
const FLIGHT_SPEED_PX_PER_SEC = 900
const SHOW_TRAJECTORY_DEBUG = false

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
  const hasQuery = query.replace(/\s/g, '').length >= 2

  return allBubbles.value.map(bubble => ({
    ...bubble,
    matches: hasQuery && bubble.fullName.toLowerCase().includes(query),
    attendanceState: getBubbleAttendanceState(bubble),
    hasQuery
  }))
})

function getBubbleAttendanceState(bubble) {
  if (bubble.type === 'individual') {
    return bubble.data.attending === true ? 'yes' : 'other'
  }

  const guests = Array.isArray(bubble.data?.guests) ? bubble.data.guests : []
  if (guests.length === 0) return 'other'

  const hasAtLeastOneConfirmed = guests.some(guest => guest.attending === true)
  return hasAtLeastOneConfirmed ? 'yes' : 'other'
}

// Small visible helper list so search results are always on screen.
const matchingBubbles = computed(() =>
  filteredBubbles.value.filter(bubble => bubble.matches).slice(0, 10)
)

const singleMatchedGuestBubble = computed(() => {
  if (searchQuery.value.trim().length === 0) return null
  if (matchingBubbles.value.length !== 1) return null
  const bubble = matchingBubbles.value[0]
  return bubble.type === 'individual' ? bubble : null
})

const showSingleGuestActions = computed(() => {
  const bubble = singleMatchedGuestBubble.value
  if (!bubble) return false
  const query = searchQuery.value.toLowerCase().trim()
  const isExactMatch = bubble.fullName.toLowerCase() === query
  if (!isExactMatch) return false
  return Boolean(dockedBubbleIds.value[bubble.id])
})

const showFamilyDetailExactMatch = computed(() => {
  if (selectedType.value !== 'family' || !selectedItem.value) return false
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return false
  return selectedItem.value.family_name?.toLowerCase() === query
})

/**
 * Split bubbles into left/right groups with unique membership (no duplicates).
 */
const trackBubbles = computed(() => {
  const left = []
  const right = []

  filteredBubbles.value.forEach((bubble, index) => {
    if (index % 2 === 0) {
      left.push(bubble)
    } else {
      right.push(bubble)
    }
  })

  return { left, right }
})

const leftTrackBubbles = computed(() => trackBubbles.value.left)
const rightTrackBubbles = computed(() => trackBubbles.value.right)
const renderedBubbles = computed(() => [...leftTrackBubbles.value, ...rightTrackBubbles.value])

/**
 * Build a sampled ellipse path around a custom center.
 * We keep a full closed path so GSAP can loop continuously;
 * clipping exposes each side as a half-moon.
 */
function buildTrajectoryPath(centerX, centerY, radiusX, radiusY) {
  const points = []

  for (let i = 0; i < PATH_SAMPLES; i++) {
    const t = (i / PATH_SAMPLES) * 2 * Math.PI
    const x = centerX + radiusX * Math.cos(t)
    const y = centerY + radiusY * Math.sin(t)
    points.push([x, y])
  }

  const pathParts = points.map((point, i) =>
    i === 0 ? `M ${point[0]} ${point[1]}` : `L ${point[0]} ${point[1]}`
  )

  return pathParts.join(' ') + ' Z'
}

// Left circle center is outside to the left; right circle center is outside to the right.
const leftTrajectoryPathData = computed(() => {
  const radiusX = isMobile.value ? TRAJECTORY_RADIUS_X_MOBILE : TRAJECTORY_RADIUS_X_DESKTOP
  const radiusY = isMobile.value ? TRAJECTORY_RADIUS_Y_MOBILE : TRAJECTORY_RADIUS_Y_DESKTOP
  const sideOffset = isMobile.value ? TRAJECTORY_SIDE_OFFSET_MOBILE : TRAJECTORY_SIDE_OFFSET_DESKTOP
  const centerY = isMobile.value ? TRAJECTORY_CENTER_Y_MOBILE : 50

  return buildTrajectoryPath(-sideOffset, centerY, radiusX, radiusY)
})

const rightTrajectoryPathData = computed(() => {
  const radiusX = isMobile.value ? TRAJECTORY_RADIUS_X_MOBILE : TRAJECTORY_RADIUS_X_DESKTOP
  const radiusY = isMobile.value ? TRAJECTORY_RADIUS_Y_MOBILE : TRAJECTORY_RADIUS_Y_DESKTOP
  const sideOffset = isMobile.value ? TRAJECTORY_SIDE_OFFSET_MOBILE : TRAJECTORY_SIDE_OFFSET_DESKTOP
  const centerY = isMobile.value ? TRAJECTORY_CENTER_Y_MOBILE : 50

  return buildTrajectoryPath(100 + sideOffset, centerY, radiusX, radiusY)
})

function setBubbleRef(el, id) {
  if (el) {
    bubbleRefs.value[id] = el
  } else {
    delete bubbleRefs.value[id]
  }
}

function setChipRef(el, id) {
  if (el) {
    chipRefs.value[id] = el
  } else {
    delete chipRefs.value[id]
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

function getBubbleVisualElement(bubbleElement) {
  if (!bubbleElement) return null
  return bubbleElement.querySelector('.bubble-visual')
}

function lerp(a, b, t) {
  return a + (b - a) * t
}

function placeCloneBetweenRects(clone, fromRect, toRect, t) {
  const fromCx = fromRect.left + fromRect.width / 2
  const fromCy = fromRect.top + fromRect.height / 2
  const toCx = toRect.left + toRect.width / 2
  const toCy = toRect.top + toRect.height / 2

  const width = lerp(fromRect.width, toRect.width, t)
  const height = lerp(fromRect.height, toRect.height, t)
  const cx = lerp(fromCx, toCx, t)
  const cy = lerp(fromCy, toCy, t)

  gsap.set(clone, {
    left: cx - width / 2,
    top: cy - height / 2,
    width,
    height,
    x: 0,
    y: 0,
    scale: 1,
    rotation: 0
  })
}

/**
 * Create a single rotation tween for one bubble.
 */
function createBubbleRotationTween(bubbleId, slot, paused = false, elementOverride = null) {
  const el = elementOverride ||
    bubbleRefs.value[bubbleId] ||
    ringsContainer.value?.querySelector(`[data-bubble-id="${bubbleId}"]`)
  if (!el || !slot) return null

  return gsap.to(el, {
    motionPath: {
      path: slot.pathElement,
      align: slot.pathElement,
      alignOrigin: [0.5, 0.5],
      start: slot.startProgress,
      end: slot.startProgress + slot.direction
    },
    duration: ROTATION_DURATION,
    ease: 'none',
    repeat: -1,
    paused
  })
}

function killRotations() {
  rotationGeneration++
  bubbleTweens.forEach(tween => tween.kill())
  bubbleTweens.clear()
  bubbleSlots.clear()
}

/**
 * Open the chosen bubble.
 * Individuals get a short focus animation before switching to detail view.
 */
function selectBubble(bubble) {
  if (bubble.type === 'individual') {
    searchQuery.value = bubble.fullName
    return
  }

  const normalizedQuery = searchQuery.value.toLowerCase().trim()
  const isStillMatch = normalizedQuery.length > 0 &&
    bubble.fullName.toLowerCase().includes(normalizedQuery)

  // Clean up flight state only when bubble is not currently a search match.
  // If still matched, keep the current visual state to avoid restart/jump.
  const flightState = flyingBubbles.get(bubble.id)
  if (flightState && !isStillMatch) {
    if (flightState.tween) flightState.tween.kill()
    if (flightState.clone && flightState.clone.parentNode) flightState.clone.remove()
    flyingBubbles.delete(bubble.id)
    delete dockedBubbleIds.value[bubble.id]
    const el = bubbleRefs.value[bubble.id]
    if (el) gsap.set(el, { autoAlpha: 1 })
  }

  searchQuery.value = bubble.fullName
  selectedItem.value = bubble.data
  selectedType.value = bubble.type
}

function clearSelection() {
  selectedItem.value = null
  selectedType.value = null
}

function clearSearch() {
  inlineGuestError.value = ''
  searchQuery.value = ''
  nextTick(() => searchInput.value?.blur())
}

async function setSingleGuestAttendance(bubble, attending) {
  if (!bubble || bubble.type !== 'individual') return
  if (inlineGuestLoading.value) return
  if (bubble.data.attending === attending) return

  if (sessionStorage.getItem('rsvp_updated') === 'pending') {
    if (!window.confirm(`Stai modificando la partecipazione di ${bubble.data.name}.\nClicca OK per procedere comunque.`)) return
    sessionStorage.setItem('rsvp_updated', 'confirmed')
  }
  inlineGuestError.value = ''
  inlineGuestLoading.value = true
  try {
    const updated = await updateGuest(bubble.data.id, { attending })
    if (!sessionStorage.getItem('rsvp_updated')) sessionStorage.setItem('rsvp_updated', 'pending')
    updateIndividual(updated)
  } catch (error) {
    inlineGuestError.value = 'Errore nel salvataggio. Riprova.'
    console.error('Failed to update RSVP inline:', error)
  } finally {
    inlineGuestLoading.value = false
  }
}

/**
 * Create one track of per-bubble tweens:
 * 1) snap bubbles to evenly distributed start positions
 * 2) create individual rotation tweens after snap completes.
 */
function initializeTrackRotation({ key, pathElement, containerElement, direction }) {
  if (!pathElement || !containerElement) return

  const bubbleElements = containerElement.querySelectorAll('.rsvp-bubble')
  if (!bubbleElements || bubbleElements.length === 0) return

  const gen = rotationGeneration

  Array.from(bubbleElements).forEach((element, index) => {
    const bubbleId = element.dataset.bubbleId
    const startProgress = index / bubbleElements.length
    bubbleRefs.value[bubbleId] = element

    // Store slot metadata for later flight-back recreation
    bubbleSlots.set(bubbleId, {
      track: key,
      slotIndex: index,
      startProgress,
      direction,
      pathElement
    })

    // Kill any existing tweens on this element
    gsap.killTweensOf(element)

    // Snap animation to initial position
    gsap.to(element, {
      motionPath: {
        path: pathElement,
        align: pathElement,
        alignOrigin: [0.5, 0.5],
        start: startProgress,
        end: startProgress
      },
      duration: 0.8,
      ease: 'power2.out',
      onComplete: () => {
        // Guard against stale callbacks after killRotations
        if (gen !== rotationGeneration) return

        const rotTween = createBubbleRotationTween(
          bubbleId,
          bubbleSlots.get(bubbleId),
          false,
          element
        )
        if (rotTween) bubbleTweens.set(bubbleId, rotTween)
      }
    })
  })
}

/**
 * Initialize visible tracks:
 * - desktop: left and right with opposite directions
 * - mobile: left and right with opposite directions.
 */
function initializeRotation() {
  killRotations()
  const gen = rotationGeneration

  initializeTrackRotation({
    key: 'right',
    pathElement: rightPath.value,
    containerElement: rightTrackContainer.value,
    direction: 1
  })

  initializeTrackRotation({
    key: 'left',
    pathElement: leftPath.value,
    containerElement: leftTrackContainer.value,
    direction: -1
  })

  // Fallback: ensure every slotted bubble has an active rotation tween.
  // This covers rare missed onComplete callbacks during rapid relayouts.
  setTimeout(() => {
    if (gen !== rotationGeneration) return
    bubbleSlots.forEach((slot, bubbleId) => {
      if (bubbleTweens.has(bubbleId)) return
      const rotTween = createBubbleRotationTween(bubbleId, slot)
      if (rotTween) bubbleTweens.set(bubbleId, rotTween)
    })
  }, 900)
}

/**
 * Apply search emphasis:
 * - matching bubbles are highlighted
 * - non matching bubbles are muted
 * - bubbles in flight are skipped.
 */
function updateBubblePositions() {
  const bubbleElements = ringsContainer.value?.querySelectorAll('.rsvp-bubble')
  if (!bubbleElements || bubbleElements.length === 0) return

  const hasQuery = searchQuery.value.trim().replace(/\s/g, '').length >= 2

  if (!hasQuery) {
    bubbleElements.forEach(element => {
      const bubbleId = element.dataset.bubbleId
      if (flyingBubbles.has(bubbleId)) return
      const visualElement = getBubbleVisualElement(element)
      if (!visualElement) return

      // Avoid heavy animated styles while rings are rotating continuously.
      gsap.set(visualElement, {
        autoAlpha: 1,
        backgroundColor: '#F5F2EB',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
      })
    })
    return
  }

  renderedBubbles.value.forEach((bubble) => {
    const element = getBubbleElement(bubble.id, bubbleElements)
    if (!element) return
    if (flyingBubbles.has(bubble.id)) return
    const visualElement = getBubbleVisualElement(element)
    if (!visualElement) return

    if (bubble.matches) {
      gsap.set(visualElement, {
        autoAlpha: 1,
        backgroundColor: '#9DAD8F',
        boxShadow: '0 10px 15px -5px rgba(61, 79, 61, 0.22), 0 4px 6px -2px rgba(61, 79, 61, 0.18)'
      })
    } else {
      gsap.set(visualElement, {
        autoAlpha: 0.35,
        backgroundColor: '#F5F2EB',
        boxShadow: '0 3px 5px -1px rgba(0, 0, 0, 0.08), 0 1px 3px -1px rgba(0, 0, 0, 0.05)'
      })
    }
  })
}

// ---------------------------------------------------------------------------
// Flight animation functions
// ---------------------------------------------------------------------------

/**
 * Animate a bubble from its orbit position to the chip area.
 */
function flyBubbleOut(bubbleId) {
  if (flyingBubbles.has(bubbleId)) return

  const el = bubbleRefs.value[bubbleId]
  if (!el) return

  // Keep orbit running and animate a visual clone to the chip area.
  // nextTick ensures Vue has rendered chip elements before rAF tries to read their rects.
  nextTick(() => requestAnimationFrame(() => {
    // Reduced-motion: instant dock without animation
    if (prefersReducedMotion.value) {
      gsap.set(el, { autoAlpha: 0 })
      flyingBubbles.set(bubbleId, { phase: 'docked', clone: null, tween: null, dockRect: null })
      dockedBubbleIds.value[bubbleId] = true
      return
    }

    const chipEl = chipRefs.value[bubbleId]
    if (!chipEl) {
      return
    }

    const sourceRect = el.getBoundingClientRect()
    const targetRect = chipEl.getBoundingClientRect()

    // Create clone in overlay at exact source position
    const clone = el.cloneNode(true)
    clone.removeAttribute('data-bubble-id')
    clone.style.position = 'fixed'
    clone.style.margin = '0'
    clone.style.pointerEvents = 'none'
    clone.style.zIndex = '999'
    clone.style.transformOrigin = 'center center'
    flightOverlay.value.appendChild(clone)

    const sourceCx = sourceRect.left + sourceRect.width / 2
    const sourceCy = sourceRect.top + sourceRect.height / 2
    const targetCx = targetRect.left + targetRect.width / 2
    const targetCy = targetRect.top + targetRect.height / 2
    const distance = Math.hypot(targetCx - sourceCx, targetCy - sourceCy)
    const flightDuration = Math.max(0.2, distance / FLIGHT_SPEED_PX_PER_SEC)

    // Set clone to exact pixel position and size of original (start invisible)
    gsap.set(clone, {
      left: sourceRect.left + 'px',
      top: sourceRect.top + 'px',
      width: sourceRect.width + 'px',
      height: sourceRect.height + 'px',
      x: 0,
      y: 0,
      scale: 1,
      rotation: 0,
      opacity: 0,
      visibility: 'visible'
    })

    const flightStateObj = { phase: 'flying-out', clone, tween: null, dockRect: null }
    flyingBubbles.set(bubbleId, flightStateObj)

    const syncCloneToLive = (t) => {
      const liveSourceRect = el.getBoundingClientRect()
      const liveChipEl = chipRefs.value[bubbleId]
      const liveTargetRect = liveChipEl ? liveChipEl.getBoundingClientRect() : targetRect
      placeCloneBetweenRects(clone, liveSourceRect, liveTargetRect, t)
    }

    // Frame-0 sync: clone starts exactly from the current rotating bubble.
    syncCloneToLive(0)
    gsap.to(clone, { opacity: 1, duration: 0.06, overwrite: 'auto' })
    gsap.set(el, { autoAlpha: 0 })

    const progressObj = { t: 0 }
    flightStateObj.tween = gsap.to(progressObj, {
      t: 1,
      duration: flightDuration,
      ease: 'none',
      overwrite: 'auto',
      onUpdate: () => {
        syncCloneToLive(progressObj.t)
      },
      onComplete: () => {
        clone.remove()
        const state = flyingBubbles.get(bubbleId)
        if (state) {
          state.phase = 'docked'
          state.clone = null
          state.tween = null
          state.dockRect = targetRect
        }
        dockedBubbleIds.value[bubbleId] = true
      }
    })
  }))
}

/**
 * Animate a bubble from the chip area back to its orbit position.
 */
function flyBubbleBack(bubbleId) {
  const state = flyingBubbles.get(bubbleId)
  if (!state) return

  // Kill any in-progress flight tween
  if (state.tween) state.tween.kill()

  const el = bubbleRefs.value[bubbleId]
  if (!el) {
    if (state.clone && state.clone.parentNode) state.clone.remove()
    flyingBubbles.delete(bubbleId)
    delete dockedBubbleIds.value[bubbleId]
    return
  }

  // Reduced-motion: instant return without animation
  if (prefersReducedMotion.value) {
    if (state.clone && state.clone.parentNode) state.clone.remove()
    flyingBubbles.delete(bubbleId)
    delete dockedBubbleIds.value[bubbleId]
    gsap.set(el, { autoAlpha: 1 })
    return
  }

  // Determine source position (clone if mid-flight, chip if docked)
  let sourceRect
  if (state.clone && state.clone.parentNode) {
    sourceRect = state.clone.getBoundingClientRect()
    state.clone.remove()
  } else if (state.phase === 'docked') {
    const chipEl = chipRefs.value[bubbleId]
    if (chipEl) {
      sourceRect = chipEl.getBoundingClientRect()
    } else if (state.dockRect) {
      sourceRect = state.dockRect
    }
  }

  delete dockedBubbleIds.value[bubbleId]

  if (!sourceRect) {
    // Fallback: no source available, just clear docked state.
    flyingBubbles.delete(bubbleId)
    gsap.set(el, { autoAlpha: 1 })
    return
  }

  // Target is the bubble's live position on the rotating ring.
  const targetRect = el.getBoundingClientRect()

  // Create return-flight clone
  const clone = el.cloneNode(true)
  clone.removeAttribute('data-bubble-id')
  clone.style.position = 'fixed'
  clone.style.margin = '0'
  clone.style.pointerEvents = 'none'
  clone.style.zIndex = '999'
  clone.style.transformOrigin = 'center center'
  flightOverlay.value.appendChild(clone)

  const sourceCx = sourceRect.left + sourceRect.width / 2
  const sourceCy = sourceRect.top + sourceRect.height / 2
  const targetCx = targetRect.left + targetRect.width / 2
  const targetCy = targetRect.top + targetRect.height / 2
  const distance = Math.hypot(targetCx - sourceCx, targetCy - sourceCy)
  const flightDuration = Math.max(0.2, distance / FLIGHT_SPEED_PX_PER_SEC)

  gsap.set(clone, {
    left: sourceRect.left + 'px',
    top: sourceRect.top + 'px',
    width: sourceRect.width + 'px',
    height: sourceRect.height + 'px',
    x: 0,
    y: 0,
    scale: 1,
    rotation: 0,
    opacity: 1,
    visibility: 'visible'
  })

  state.phase = 'flying-back'
  state.clone = clone
  const progressObj = { t: 0 }
  state.tween = gsap.to(progressObj, {
    t: 1,
    duration: flightDuration,
    ease: 'none',
    overwrite: 'auto',
    onUpdate: () => {
      const liveTargetRect = el.getBoundingClientRect()
      placeCloneBetweenRects(clone, sourceRect, liveTargetRect, progressObj.t)
    },
    onComplete: () => {
      clone.remove()
      gsap.set(el, { autoAlpha: 1 })
      const visual = getBubbleVisualElement(el)
      if (visual) {
        gsap.set(visual, {
          backgroundColor: '#F5F2EB',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
        })
      }
      flyingBubbles.delete(bubbleId)
    }
  })
}

/**
 * Immediately cancel all flights and restore bubbles to orbiting state.
 */
function killAllFlights() {
  staggerFlightTimers.forEach(timerId => clearTimeout(timerId))
  staggerFlightTimers.clear()

  flyingBubbles.forEach((state, bubbleId) => {
    if (state.tween) state.tween.kill()
    if (state.clone && state.clone.parentNode) state.clone.remove()
    const el = bubbleRefs.value[bubbleId]
    if (el) gsap.set(el, { autoAlpha: 1 })
  })
  flyingBubbles.clear()
  dockedBubbleIds.value = {}
}

/**
 * Diff current matchingBubbles against flyingBubbles and trigger flights.
 * New matches fly out with stagger; removed matches fly back.
 */
function reconcileFlights() {
  reconcileGeneration++
  const generation = reconcileGeneration

  // Cancel pending staggered launches from older queries
  staggerFlightTimers.forEach(timerId => clearTimeout(timerId))
  staggerFlightTimers.clear()

  const matchIds = new Set(matchingBubbles.value.map(b => b.id))

  // Fly back bubbles that no longer match
  const toFlyBack = []
  flyingBubbles.forEach((_state, bubbleId) => {
    if (!matchIds.has(bubbleId)) {
      toFlyBack.push(bubbleId)
    }
  })
  toFlyBack.forEach(id => flyBubbleBack(id))

  // Fly out new matches with 50ms stagger
  let staggerDelay = 0
  matchingBubbles.value.forEach(bubble => {
    if (!flyingBubbles.has(bubble.id)) {
      const id = bubble.id
      if (staggerDelay === 0) {
        flyBubbleOut(id)
      } else {
        const timerId = setTimeout(() => {
          staggerFlightTimers.delete(timerId)
          if (generation !== reconcileGeneration) return
          flyBubbleOut(id)
        }, staggerDelay)
        staggerFlightTimers.add(timerId)
      }
      staggerDelay += 50
    }
  })
}

// ---------------------------------------------------------------------------
// Ring lifecycle
// ---------------------------------------------------------------------------

function refreshRings() {
  if (loading.value) return

  killAllFlights()

  nextTick(() => {
    initializeRotation()
    setTimeout(() => {
      updateBubblePositions()
      if (searchQuery.value.trim().length > 0) {
        reconcileFlights()
      }
    }, 40)
  })
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

onMounted(async () => {
  await fetchData()
  await nextTick()

  prefersReducedMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches

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

  const mediaQuery = window.matchMedia('(max-width: 767px)')
  isMobile.value = mediaQuery.matches

  const mediaHandler = (event) => {
    isMobile.value = event.matches
  }

  if (typeof mediaQuery.addEventListener === 'function') {
    mediaQuery.addEventListener('change', mediaHandler)
    removeMediaListener = () => mediaQuery.removeEventListener('change', mediaHandler)
  } else {
    mediaQuery.addListener(mediaHandler)
    removeMediaListener = () => mediaQuery.removeListener(mediaHandler)
  }

  refreshRings()
})

watch(searchQuery, () => {
  if (loading.value) return
  inlineGuestError.value = ''

  const normalizedQuery = searchQuery.value.toLowerCase().trim()
  if (selectedItem.value) {
    const selectedLabel = selectedType.value === 'family'
      ? selectedItem.value?.family_name
      : selectedItem.value?.name

    if (!selectedLabel || normalizedQuery !== selectedLabel.toLowerCase()) {
      clearSelection()
    }
  }

  updateBubblePositions()

  if (reconcileTimer) clearTimeout(reconcileTimer)
  staggerFlightTimers.forEach(timerId => clearTimeout(timerId))
  staggerFlightTimers.clear()

  if (searchQuery.value.trim().length === 0) {
    // Search cleared: fly everything back immediately (chips still in DOM pre-flush)
    reconcileFlights()
  } else {
    reconcileTimer = setTimeout(() => reconcileFlights(), 300)
  }
})

watch(
  () => [isMobile.value, allBubbles.value.length],
  () => {
    refreshRings()
  }
)

onBeforeUnmount(() => {
  if (reconcileTimer) clearTimeout(reconcileTimer)
  staggerFlightTimers.forEach(timerId => clearTimeout(timerId))
  staggerFlightTimers.clear()
  killAllFlights()
  killRotations()

  if (removeMediaListener) {
    removeMediaListener()
    removeMediaListener = null
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

  .single-match-pulse {
    animation: none !important;
  }
}

.single-match-pulse {
  animation: single-chip-pulse 1.1s ease-in-out infinite;
}

.yes-border {
  border-width: 3px;
  border-color: rgba(61, 79, 61, 0.98);
  outline: 2px solid rgba(128, 157, 111, 0.85);
  outline-offset: 1px;
  filter: drop-shadow(0 0 10px rgba(128, 157, 111, 0.65));
}

.script-glyph-safe {
  display: inline-block;
  transform: translateY(0.08em);
  padding-top: 0.12em;
}

@keyframes single-chip-pulse {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(61, 79, 61, 0.26);
  }
  70% {
    transform: scale(1.04);
    box-shadow: 0 0 0 10px rgba(61, 79, 61, 0);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(61, 79, 61, 0);
  }
}
</style>
