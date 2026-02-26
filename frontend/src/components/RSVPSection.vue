<template>
  <section ref="sectionEl" class="relative min-h-screen py-20 px-4">
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
          <div
            class="mx-auto max-w-md relative transition-[height,margin] duration-200"
            :class="selectedItem ? 'mt-1 h-2' : 'mt-3 h-16'"
          >
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
          </div>
        </div>

        <div class="relative min-h-[1px]">
          <!-- Detail View: anchored directly below search/chips -->
          <Transition name="fade">
            <div v-if="selectedItem" ref="detailPanel" class="absolute left-1/2 -translate-x-1/2 top-0 w-full max-w-xl px-4 md:px-0 z-20">
              <RSVPFamilyCard
                v-if="selectedType === 'family'"
                :family="selectedItem"
                :show-title="!showFamilyDetailExactMatch"
                @updated="updateFamilyGuest"
                @saved="scrollToSearchArea"
                @close="clearSelection"
                class="w-full"
              />

              <RSVPCard
                v-if="selectedType === 'individual'"
                :guest="selectedItem"
                @updated="updateIndividual"
                @saved="scrollToSearchArea"
                @completed="handleIndividualCompleted"
                @close="clearSelection"
                class="w-full"
              />
            </div>
          </Transition>
        </div>

        <div class="mx-auto max-w-md h-7 -mt-1 mb-2 relative pointer-events-none">
          <Transition name="fade">
            <p
              v-if="showDragHint"
              class="absolute inset-0 flex items-center justify-center"
            >
              <span class="drag-hint-nudge flex items-center justify-center gap-2 text-forest/70 font-serif text-sm md:text-base">
                <span class="text-base leading-none">↔</span>
                <span>Trascina orizzontalmente</span>
              </span>
            </p>
          </Transition>
        </div>

        <div class="relative mt-3">
          <div
            :class="selectedItem ? 'pointer-events-none opacity-45 transition-opacity duration-300' : 'transition-opacity duration-300'"
          >
            <!-- Two clipped side tracks on both desktop and mobile. -->
          <div
            ref="ringsContainer"
              class="relative w-screen max-w-screen left-1/2 -translate-x-1/2 h-[68vh] min-h-[28rem] md:h-[36rem] overflow-x-hidden overflow-y-visible select-none touch-pan-y"
              :class="[activeRingDrag ? 'cursor-grabbing' : 'cursor-grab', !bubblesInteractive ? 'pointer-events-none' : '']"
              @pointerdown="onRingPointerDown"
              @pointermove="onRingPointerMove"
              @pointerup="onRingPointerUp"
              @pointercancel="onRingPointerUp"
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
import { RSVP_EVENT_OPTIONS, getGuestAttendanceState, isDeclinedState } from '../constants/rsvp'

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
const sectionEl = ref(null)
const detailPanel = ref(null)
const bubblesInteractive = ref(true)
let removeScrollListener = null

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
const keepSelectionOnSearchClear = ref(false)

// Per-bubble rotation tweens and slot metadata.
const bubbleTweens = new Map()
const bubbleSlots = new Map()
const inertiaTweens = new Map()
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
const inlineSingleGuestExpanded = ref(false)
const singleGuestAttendanceState = computed(() => (
  singleMatchedGuestBubble.value ? getGuestAttendanceState(singleMatchedGuestBubble.value.data) : null
))
const singleGuestOverallChoice = computed(() => {
  const state = singleGuestAttendanceState.value
  if (!state) return null
  if (isDeclinedState(state)) return 'decline'
  if (state.attend_ceremony === true || state.attend_lunch === true) return 'attend'
  return null
})
const showSingleGuestEventRows = computed(() => (
  inlineSingleGuestExpanded.value || singleGuestOverallChoice.value === 'attend'
))

// Animation/layout constants for side trajectories.
const ROTATION_DURATION = 60
const TRAJECTORY_RADIUS_X_DESKTOP = 90
const TRAJECTORY_RADIUS_Y_DESKTOP = 44
const TRAJECTORY_SIDE_OFFSET_DESKTOP = 36

const TRAJECTORY_RADIUS_X_MOBILE = 84
const TRAJECTORY_RADIUS_Y_MOBILE = 82
const TRAJECTORY_SIDE_OFFSET_MOBILE = 34
const TRAJECTORY_CENTER_Y_MOBILE = 12
const PATH_SAMPLES = 200
const FLIGHT_SPEED_PX_PER_SEC = 900
const SHOW_TRAJECTORY_DEBUG = false
const DRAG_PROGRESS_PER_PIXEL = 0.0018
const DRAG_START_THRESHOLD_PX = 6
const DRAG_INERTIA_VELOCITY_THRESHOLD = 0.06
const DRAG_INERTIA_DISTANCE_FACTOR = 0.42
const DRAG_INERTIA_MAX_TURNS = 0.34
const DRAG_INERTIA_MIN_DURATION = 0.35
const DRAG_INERTIA_MAX_DURATION = 1.1

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
  return false
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
const activeRingDrag = ref(null)
const showDragHint = ref(true)

let suppressBubbleClickUntil = 0

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
  killAllInertia(false)
  bubbleTweens.forEach(tween => tween.kill())
  bubbleTweens.clear()
  bubbleSlots.clear()
}

/**
 * Open the chosen bubble.
 * Individuals get a short focus animation before switching to detail view.
 */
function selectBubble(bubble) {
  if (Date.now() < suppressBubbleClickUntil) return

  if (bubble.type === 'individual') {
    selectedItem.value = bubble.data
    selectedType.value = bubble.type
    keepSelectionOnSearchClear.value = true
    searchQuery.value = ''
    scheduleDetailPanelScroll()
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

  selectedItem.value = bubble.data
  selectedType.value = bubble.type
  keepSelectionOnSearchClear.value = true
  searchQuery.value = ''
  scheduleDetailPanelScroll()
}

function scheduleDetailPanelScroll() {
  nextTick(() => {
    const panel = detailPanel.value
    if (!panel) return

    const rect = panel.getBoundingClientRect()
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0
    if (!viewportHeight) return

    const desiredTop = Math.round(viewportHeight * 0.18)
    const currentTop = rect.top
    const delta = currentTop - desiredTop

    // Avoid tiny jitter when already in a good position.
    if (Math.abs(delta) < 24) return

    const currentScrollY = window.scrollY || window.pageYOffset || 0
    const targetTop = Math.max(0, currentScrollY + delta)
    window.scrollTo({ top: targetTop, behavior: 'smooth' })
  })
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

function scrollToSearchArea() {
  nextTick(() => {
    const target = searchInput.value || header.value || sectionEl.value
    if (!target || typeof target.scrollIntoView !== 'function') return
    target.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

function handleIndividualCompleted() {
  clearSelection()
  clearSearch()
}

function wrap01(value) {
  let wrapped = value % 1
  if (wrapped < 0) wrapped += 1
  return wrapped
}

function withTrackTweens(track, callback) {
  bubbleSlots.forEach((slot, bubbleId) => {
    if (slot.track !== track) return
    const tween = bubbleTweens.get(bubbleId)
    if (!tween) return
    callback(tween, slot, bubbleId)
  })
}

function markDragHintSeen() {
  if (!showDragHint.value) return
  showDragHint.value = false
}

function shiftTrackProgressBy(track, progressDelta) {
  if (progressDelta === 0) return
  withTrackTweens(track, (tween) => {
    tween.progress(wrap01(tween.progress() + progressDelta))
  })
}

function killTrackInertia(track, shouldResume = true) {
  const inertiaTween = inertiaTweens.get(track)
  if (!inertiaTween) return
  inertiaTween.kill()
  inertiaTweens.delete(track)
  if (shouldResume) {
    withTrackTweens(track, (tween) => tween.play())
  }
}

function killAllInertia(shouldResume = true) {
  Array.from(inertiaTweens.keys()).forEach(track => killTrackInertia(track, shouldResume))
}

function startTrackInertia(track, velocityProgressPerSec) {
  const speed = Math.abs(velocityProgressPerSec)
  if (prefersReducedMotion.value || speed < DRAG_INERTIA_VELOCITY_THRESHOLD) {
    return false
  }

  const targetDelta = Math.max(
    -DRAG_INERTIA_MAX_TURNS,
    Math.min(DRAG_INERTIA_MAX_TURNS, velocityProgressPerSec * DRAG_INERTIA_DISTANCE_FACTOR)
  )
  if (targetDelta === 0) return false

  const duration = Math.max(
    DRAG_INERTIA_MIN_DURATION,
    Math.min(
      DRAG_INERTIA_MAX_DURATION,
      DRAG_INERTIA_MIN_DURATION + Math.abs(targetDelta) * 1.8
    )
  )

  killTrackInertia(track, false)

  const proxy = { progress: 0 }
  let lastProgress = 0

  const tween = gsap.to(proxy, {
    progress: targetDelta,
    duration,
    ease: 'power3.out',
    overwrite: 'auto',
    onUpdate: () => {
      const step = proxy.progress - lastProgress
      lastProgress = proxy.progress
      shiftTrackProgressBy(track, step)
    },
    onComplete: () => {
      inertiaTweens.delete(track)
      withTrackTweens(track, (rotTween) => rotTween.play())
    }
  })

  inertiaTweens.set(track, tween)
  return true
}

function onRingPointerDown(event) {
  if (loading.value) return
  if (event.pointerType === 'mouse' && event.button !== 0) return

  const container = ringsContainer.value
  if (!container) return

  const rect = container.getBoundingClientRect()
  const track = event.clientX < rect.left + rect.width / 2 ? 'left' : 'right'
  const nowTs = event.timeStamp || performance.now()

  activeRingDrag.value = {
    pointerId: event.pointerId,
    track,
    lastX: event.clientX,
    lastTs: nowTs,
    velocityProgressPerSec: 0,
    moved: false
  }

  killTrackInertia(track, false)
  withTrackTweens(track, (tween) => tween.pause())

}

function onRingPointerMove(event) {
  const drag = activeRingDrag.value
  if (!drag || drag.pointerId !== event.pointerId) return

  const nowTs = event.timeStamp || performance.now()
  const deltaX = event.clientX - drag.lastX
  const deltaTimeSec = Math.max((nowTs - drag.lastTs) / 1000, 0.001)
  drag.lastX = event.clientX
  drag.lastTs = nowTs

  if (!drag.moved && Math.abs(deltaX) >= DRAG_START_THRESHOLD_PX) {
    drag.moved = true
    markDragHintSeen()
    // Capture pointer only after horizontal intent is confirmed, so vertical
    // scroll gestures are not accidentally intercepted before the threshold.
    const cont = ringsContainer.value
    if (cont && typeof cont.setPointerCapture === 'function') {
      try { cont.setPointerCapture(event.pointerId) } catch (_) {}
    }
  }
  if (!drag.moved || deltaX === 0) return

  event.preventDefault()

  const trackSign = drag.track === 'left' ? -1 : 1
  const progressDelta = deltaX * DRAG_PROGRESS_PER_PIXEL * trackSign
  const instantVelocity = progressDelta / deltaTimeSec
  drag.velocityProgressPerSec = drag.velocityProgressPerSec * 0.65 + instantVelocity * 0.35
  shiftTrackProgressBy(drag.track, progressDelta)
}

function onRingPointerUp(event) {
  const drag = activeRingDrag.value
  if (!drag || drag.pointerId !== event.pointerId) return

  const container = ringsContainer.value
  if (container && typeof container.releasePointerCapture === 'function') {
    try {
      container.releasePointerCapture(event.pointerId)
    } catch (_error) {
      // Ignore invalid release attempts.
    }
  }

  if (drag.moved) {
    suppressBubbleClickUntil = Date.now() + 180
  }

  const hasInertia = drag.moved && startTrackInertia(drag.track, drag.velocityProgressPerSec)
  if (!hasInertia) {
    withTrackTweens(drag.track, (tween) => tween.play())
  }
  activeRingDrag.value = null
}

function cancelRingDrag() {
  const drag = activeRingDrag.value
  if (drag) {
    withTrackTweens(drag.track, (tween) => tween.play())
  }
  activeRingDrag.value = null
  killAllInertia()
}

async function setSingleGuestEventAttendance(bubble, field, value) {
  if (!bubble || bubble.type !== 'individual') return
  if (inlineGuestLoading.value) return
  if (getGuestAttendanceState(bubble.data)[field] === value) return

  if (sessionStorage.getItem('rsvp_updated') === 'pending') {
    if (!window.confirm(`Stai modificando la partecipazione di ${bubble.data.name}.\nClicca OK per procedere comunque.`)) return
    sessionStorage.setItem('rsvp_updated', 'confirmed')
  }
  if (value === true) inlineSingleGuestExpanded.value = true
  inlineGuestError.value = ''
  inlineGuestLoading.value = true
  try {
    const updated = await updateGuest(bubble.data.id, { [field]: value })
    if (!sessionStorage.getItem('rsvp_updated')) sessionStorage.setItem('rsvp_updated', 'pending')
    updateIndividual(updated)
  } catch (error) {
    inlineGuestError.value = 'Errore nel salvataggio. Riprova.'
    console.error('Failed to update RSVP inline:', error)
  } finally {
    inlineGuestLoading.value = false
  }
}

async function acceptSingleGuest(bubble) {
  if (!bubble || bubble.type !== 'individual') return
  if (inlineGuestLoading.value) return
  const state = getGuestAttendanceState(bubble.data)
  if (state.attend_ceremony === true && state.attend_lunch === true) {
    inlineSingleGuestExpanded.value = true
    return
  }

  if (sessionStorage.getItem('rsvp_updated') === 'pending') {
    if (!window.confirm(`Stai modificando la partecipazione di ${bubble.data.name}.\nClicca OK per procedere comunque.`)) return
    sessionStorage.setItem('rsvp_updated', 'confirmed')
  }
  inlineSingleGuestExpanded.value = true
  inlineGuestError.value = ''
  inlineGuestLoading.value = true
  try {
    const updated = await updateGuest(bubble.data.id, { attend_ceremony: true, attend_lunch: true })
    if (!sessionStorage.getItem('rsvp_updated')) sessionStorage.setItem('rsvp_updated', 'pending')
    updateIndividual(updated)
  } catch (error) {
    inlineGuestError.value = 'Errore nel salvataggio. Riprova.'
    console.error('Failed to update RSVP inline:', error)
  } finally {
    inlineGuestLoading.value = false
  }
}

async function declineSingleGuest(bubble) {
  if (!bubble || bubble.type !== 'individual') return
  if (inlineGuestLoading.value) return
  if (isDeclinedState(getGuestAttendanceState(bubble.data))) return

  if (sessionStorage.getItem('rsvp_updated') === 'pending') {
    if (!window.confirm(`Stai modificando la partecipazione di ${bubble.data.name}.\nClicca OK per procedere comunque.`)) return
    sessionStorage.setItem('rsvp_updated', 'confirmed')
  }
  inlineSingleGuestExpanded.value = false
  inlineGuestError.value = ''
  inlineGuestLoading.value = true
  try {
    const updated = await updateGuest(bubble.data.id, { attend_ceremony: false, attend_lunch: false })
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

  cancelRingDrag()
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

  const updateInteractivity = () => {
    if (!sectionEl.value) return
    const bottom = sectionEl.value.getBoundingClientRect().bottom
    bubblesInteractive.value = bottom > window.innerHeight / 3
  }

  updateInteractivity()
  window.addEventListener('scroll', updateInteractivity, { passive: true })
  removeScrollListener = () => window.removeEventListener('scroll', updateInteractivity)
})

watch(searchQuery, () => {
  if (loading.value) return
  inlineGuestError.value = ''
  inlineSingleGuestExpanded.value = false

  const normalizedQuery = searchQuery.value.toLowerCase().trim()
  if (selectedItem.value) {
    if (keepSelectionOnSearchClear.value && normalizedQuery === '') {
      keepSelectionOnSearchClear.value = false
    } else {
    const selectedLabel = selectedType.value === 'family'
      ? selectedItem.value?.family_name
      : selectedItem.value?.name

      if (!selectedLabel || normalizedQuery !== selectedLabel.toLowerCase()) {
        clearSelection()
      }
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
  cancelRingDrag()
  killAllFlights()
  killRotations()

  if (removeMediaListener) {
    removeMediaListener()
    removeMediaListener = null
  }

  if (removeScrollListener) {
    removeScrollListener()
    removeScrollListener = null
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

.drag-hint-nudge {
  animation: drag-hint-nudge 2.2s ease-in-out infinite;
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

@keyframes drag-hint-nudge {
  0% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-8px);
  }
  50% {
    transform: translateX(8px);
  }
  75% {
    transform: translateX(-4px);
  }
  100% {
    transform: translateX(0);
  }
}
</style>
