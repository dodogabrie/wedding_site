<template>
  <div class="max-w-6xl mx-auto px-2 sm:px-4 py-6">
    <!-- Header -->
    <div class="relative text-center mb-8">
      <a
        href="/"
        class="absolute left-0 top-1/2 -translate-y-1/2 flex items-center gap-1 text-forest/70 hover:text-forest transition-colors font-serif text-sm"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span class="hidden sm:inline">Home</span>
      </a>
      <h1 class="font-script text-5xl sm:text-6xl text-forest mb-2">Gallery</h1>
      <p class="font-serif text-forest/80 text-lg">Condividi i tuoi scatti della giornata</p>
    </div>

    <!-- Upload Section -->
    <div class="bg-cream rounded-2xl p-4 sm:p-6 mb-8 shadow-sm">
      <!-- Uploader Name -->
      <div v-if="!uploaderName" class="mb-4">
        <label class="block font-serif text-forest mb-1 text-sm">Il tuo nome</label>
        <div class="flex gap-2">
          <input
            v-model="nameInput"
            type="text"
            maxlength="50"
            placeholder="Come ti chiami?"
            class="flex-1 min-w-0 rounded-lg border border-sage/40 px-3 py-2 font-serif text-forest bg-white focus:outline-none focus:ring-2 focus:ring-sage"
            @keyup.enter="saveName"
          />
          <button
            @click="saveName"
            :disabled="!nameInput.trim()"
            class="px-4 py-2 rounded-lg bg-forest text-cream font-serif disabled:opacity-40 transition-opacity"
          >
            OK
          </button>
        </div>
      </div>

      <div v-else class="mb-3 flex items-center gap-2">
        <span class="font-serif text-forest/70 text-sm">
          Ciao, <strong class="text-forest">{{ uploaderName }}</strong>
        </span>
        <button @click="clearName" class="text-forest/50 hover:text-forest text-xs underline">cambia</button>
      </div>

      <!-- Upload Button -->
      <div v-if="uploaderName">
        <label
          class="flex flex-col items-center justify-center w-full h-28 border-2 border-dashed border-sage rounded-xl cursor-pointer hover:bg-sage/10 transition-colors"
        >
          <svg class="w-8 h-8 text-forest/60 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <span class="font-serif text-forest/70 text-sm">Tocca per aggiungere foto</span>
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp,image/heic,image/heif"
            multiple
            capture="environment"
            class="hidden"
            @change="onFilesSelected"
          />
        </label>

        <!-- Caption input (shown after file selection) -->
        <div v-if="pendingFiles.length > 0 && !isUploading" class="mt-3">
          <p class="font-serif text-forest/70 text-sm mb-1">
            {{ pendingFiles.length }} {{ pendingFiles.length === 1 ? 'foto selezionata' : 'foto selezionate' }}
          </p>
          <input
            v-model="captionInput"
            type="text"
            maxlength="200"
            placeholder="Aggiungi una didascalia (opzionale)"
            class="w-full rounded-lg border border-sage/40 px-3 py-2 font-serif text-forest text-sm bg-white focus:outline-none focus:ring-2 focus:ring-sage mb-2"
          />
          <button
            @click="startUpload"
            class="w-full py-2 rounded-lg bg-forest text-cream font-serif transition-opacity hover:opacity-90"
          >
            Carica {{ pendingFiles.length === 1 ? 'foto' : 'foto' }}
          </button>
        </div>

        <!-- Upload Progress -->
        <div v-if="isUploading" class="mt-3">
          <div class="flex items-center gap-2 mb-1">
            <span class="font-serif text-forest/70 text-sm">
              Caricamento {{ uploadCurrent }}/{{ uploadTotal }}...
            </span>
          </div>
          <div class="w-full bg-sage/30 rounded-full h-2">
            <div
              class="bg-forest h-2 rounded-full transition-all duration-300"
              :style="{ width: uploadProgress + '%' }"
            ></div>
          </div>
        </div>

        <!-- Upload Error -->
        <p v-if="uploadError" class="mt-2 font-serif text-red-700 text-sm">{{ uploadError }}</p>
      </div>
    </div>

    <!-- Marquee Section -->
    <div v-if="marqueePhotos.length > 0" class="marquee-wrapper mb-8 py-3">
      <div
        ref="marqueeEl"
        class="marquee-container"
        @mouseenter="marqueeHovered = true"
        @mouseleave="marqueeHovered = false"
        @mousedown.prevent="onDragStart"
        @touchstart.passive="onDragStart"
      >
        <div
          ref="marqueeTrack"
          class="marquee-track flex gap-3"
          :style="{ transform: `translateX(${marqueeOffset}px)` }"
        >
          <div
            v-for="(photo, i) in marqueeTripled"
            :key="'m-' + i"
            class="flex-shrink-0 h-24 sm:h-32 aspect-square rounded-xl overflow-hidden cursor-pointer shadow-md hover:shadow-lg transition-shadow duration-200"
            @click="onMarqueePhotoClick(photo)"
          >
            <img
              :src="photo.thumb_url"
              :alt="photo.caption || 'Wedding photo'"
              loading="lazy"
              class="w-full h-full object-cover pointer-events-none"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Section Header with Search -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
      <h2 class="font-script text-3xl text-forest">Tutte le foto</h2>
      <div class="relative w-full sm:w-72">
        <input
          v-model="searchInput"
          type="text"
          placeholder="Cerca per nome o didascalia..."
          class="w-full rounded-lg border border-sage/40 pl-9 pr-8 py-2 font-serif text-forest text-sm bg-white focus:outline-none focus:ring-2 focus:ring-sage"
        />
        <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-forest/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <button
          v-if="searchInput"
          @click="searchInput = ''"
          class="absolute right-2 top-1/2 -translate-y-1/2 text-forest/40 hover:text-forest"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Photo Grid -->
    <div v-if="photos.length > 0" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 sm:gap-3">
      <div
        v-for="photo in photos"
        :key="photo.id"
        class="relative aspect-square cursor-pointer overflow-hidden rounded-lg bg-sage/20 group"
        @click="openLightbox(photo)"
      >
        <img
          :src="photo.thumb_url"
          :alt="photo.caption || 'Wedding photo'"
          loading="lazy"
          class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        <div v-if="photo.uploader_name" class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent p-2 opacity-0 group-hover:opacity-100 transition-opacity sm:block hidden">
          <span class="text-white text-xs font-serif">{{ photo.uploader_name }}</span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!isLoading && !isSearching" class="text-center py-16">
      <p class="font-serif text-forest/60 text-lg">Nessuna foto ancora. Sii il primo a condividerne una!</p>
    </div>

    <!-- No search results -->
    <div v-else-if="!isLoading && isSearching && photos.length === 0" class="text-center py-16">
      <p class="font-serif text-forest/60 text-lg">Nessuna foto trovata</p>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-8">
      <p class="font-serif text-forest/60">Caricamento...</p>
    </div>

    <!-- Infinite Scroll Sentinel -->
    <div ref="sentinel" class="h-1"></div>

    <!-- Lightbox -->
    <Teleport to="body">
      <div
        v-if="lightboxPhoto"
        class="lightbox-overlay fixed inset-0 z-50 bg-black/90"
      >
        <!-- Sliding image strip (behind controls) -->
        <div
          ref="lbViewportEl"
          class="absolute inset-0 z-0 overflow-hidden"
          @click.self="closeLightbox"
          @touchstart.passive="onLbTouchStart"
          @touchmove.prevent="onLbTouchMove"
          @touchend.passive="onLbTouchEnd"
          @touchcancel="onLbTouchCancel"
        >
          <div
            class="lightbox-track absolute inset-0"
            :class="{ 'lightbox-animating': lbAnimating }"
            :style="lightboxTrackStyle"
            @transitionend="onLightboxTrackTransitionEnd"
          >
            <div
              v-for="slide in visibleLightboxSlides"
              :key="`lb-${slide.photo.id}`"
              class="lightbox-slide"
              :style="lightboxSlideStyle"
            >
              <img
                :src="slide.photo.full_url"
                :alt="slide.photo.caption || 'Wedding photo'"
                class="max-h-[85vh] max-w-[95vw] object-contain select-none"
                :class="{
                  'pointer-events-none': slide.index !== lightboxIndex,
                  'lightbox-media-animating': lbOverlayAnimating,
                }"
                :style="lightboxMediaStyle"
                @click.stop
              />
            </div>
          </div>
        </div>

        <!-- Close button (above slider) -->
        <button
          @click="closeLightbox"
          class="absolute top-4 right-4 z-20 text-white/80 hover:text-white p-2"
        >
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <!-- Prev button -->
        <button
          v-if="lightboxIndex > 0"
          @click.stop="slideToPhoto(-1)"
          class="absolute left-2 top-1/2 -translate-y-1/2 z-20 text-white/60 hover:text-white p-2 hidden sm:block"
        >
          <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <!-- Next button -->
        <button
          v-if="lightboxIndex < photos.length - 1"
          @click.stop="slideToPhoto(1)"
          class="absolute right-2 top-1/2 -translate-y-1/2 z-20 text-white/60 hover:text-white p-2 hidden sm:block"
        >
          <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>

        <!-- Share (mobile) / Download (desktop) button -->
        <button
          @click="sharePhoto"
          class="absolute top-4 left-4 z-20 text-white/80 hover:text-white p-2"
        >
          <!-- Share icon (mobile) -->
          <svg class="w-7 h-7 sm:hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          <!-- Download icon (desktop) -->
          <svg class="w-7 h-7 hidden sm:block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </button>

        <!-- Caption/Info -->
        <div class="absolute bottom-4 left-4 right-4 text-center z-20">
          <p v-if="lightboxPhoto.caption" class="text-white font-serif text-lg mb-1">{{ lightboxPhoto.caption }}</p>
          <p v-if="lightboxPhoto.uploader_name" class="text-white/60 font-serif text-sm">
            Foto di {{ lightboxPhoto.uploader_name }}
          </p>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { getPhotos, uploadPhoto } from '../services/photoApi.js'

const STORAGE_KEY = 'wedding_gallery_uploader_name'
const PER_PAGE = 20
const MARQUEE_MAX = 20
const LIGHTBOX_WINDOW_RADIUS = 3

// Upload state
const uploaderName = ref(localStorage.getItem(STORAGE_KEY) || '')
const nameInput = ref('')
const captionInput = ref('')
const pendingFiles = ref([])
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadCurrent = ref(0)
const uploadTotal = ref(0)
const uploadError = ref('')

// Gallery state
const photos = ref([])
const allPhotosCache = ref([])
const isLoading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const sentinel = ref(null)

// Search state
const searchInput = ref('')
const activeSearch = ref('')
let debounceTimer = null

const isSearching = computed(() => activeSearch.value.length > 0)

// Marquee state - rAF driven for seamless loop + inertia
const marqueeEl = ref(null)
const marqueeTrack = ref(null)
const marqueePhotos = computed(() => allPhotosCache.value.slice(0, MARQUEE_MAX))
// Triple the list so we have room to wrap seamlessly in both directions
const marqueeTripled = computed(() => [
  ...marqueePhotos.value,
  ...marqueePhotos.value,
  ...marqueePhotos.value,
])
const marqueeOffset = ref(0)
const marqueeHovered = ref(false)

const AUTO_SPEED = 0.15 // px per frame at 60fps
const FRICTION = 0.95
const MIN_VELOCITY = 0.1

let rafId = null
let velocity = 0
let isDragging = false
let dragStartX = 0
let dragStartOffset = 0
let dragMoved = false
let lastDragX = 0
let lastDragTime = 0

// Lightbox state
const lightboxIndex = ref(-1)
const lbViewportEl = ref(null)
const lbTrackOffsetX = ref(0)
const lbAnimating = ref(false)
const lbOverlayOffsetY = ref(0)
const lbOverlayAnimating = ref(false)
let lbTouchStartX = 0
let lbTouchStartY = 0
let lbTouchDeltaX = 0
let lbTouchDeltaY = 0
let lbGestureAxis = null
let lbTargetIndex = null

const lightboxPhoto = computed(() => {
  if (lightboxIndex.value < 0) return null
  return photos.value[lightboxIndex.value] || null
})

const lightboxTrackStyle = computed(() => {
  const width = getLightboxViewportWidth()
  const baseX = lightboxIndex.value < 0 ? 0 : -(lightboxIndex.value - lightboxWindowStart.value) * width
  return {
    width: `${visibleLightboxSlides.value.length * width}px`,
    transform: `translate3d(${baseX + lbTrackOffsetX.value}px, 0, 0)`,
  }
})

const lightboxSlideStyle = computed(() => {
  const width = getLightboxViewportWidth()
  return {
    width: `${width}px`,
  }
})

const lightboxWindowStart = computed(() => {
  if (lightboxIndex.value < 0) return 0
  const anchor = lbTargetIndex ?? lightboxIndex.value
  return Math.max(0, Math.min(lightboxIndex.value, anchor) - LIGHTBOX_WINDOW_RADIUS)
})

const lightboxWindowEnd = computed(() => {
  if (lightboxIndex.value < 0) return -1
  const anchor = lbTargetIndex ?? lightboxIndex.value
  return Math.min(
    photos.value.length - 1,
    Math.max(lightboxIndex.value, anchor) + LIGHTBOX_WINDOW_RADIUS
  )
})

const visibleLightboxSlides = computed(() => {
  if (lightboxIndex.value < 0) return []
  const slides = []
  for (let index = lightboxWindowStart.value; index <= lightboxWindowEnd.value; index += 1) {
    slides.push({ index, photo: photos.value[index] })
  }
  return slides
})

const lightboxMediaStyle = computed(() => {
  const height = lbViewportEl.value?.clientHeight || window.innerHeight || 1
  const progress = Math.min(Math.abs(lbOverlayOffsetY.value) / (height * 0.45), 1)
  const scale = 1 - progress * 0.72
  const radius = progress * 28

  return {
    transform: `scale(${Math.max(scale, 0.28)})`,
    borderRadius: `${radius}px`,
  }
})

const preloadedLightboxUrls = new Set()
const pendingLightboxPreloads = new Map()

function ensureLightboxImagePreloaded(url) {
  if (!url) return Promise.resolve()
  if (preloadedLightboxUrls.has(url)) return Promise.resolve()
  if (pendingLightboxPreloads.has(url)) return pendingLightboxPreloads.get(url)

  const task = new Promise((resolve) => {
    const img = new Image()
    img.decoding = 'async'
    const finish = () => {
      preloadedLightboxUrls.add(url)
      pendingLightboxPreloads.delete(url)
      resolve()
    }
    img.onload = async () => {
      try {
        if (typeof img.decode === 'function') {
          await img.decode()
        }
      } catch {
        // If decode fails, continue; onload already guarantees data is available.
      }
      finish()
    }
    img.onerror = () => {
      pendingLightboxPreloads.delete(url)
      resolve()
    }
    img.src = url
  })

  pendingLightboxPreloads.set(url, task)
  return task
}

function preloadNearbyLightboxPhotos(index) {
  if (index < 0) return

  const nearbyUrls = [
    photos.value[index - 1]?.full_url,
    photos.value[index]?.full_url,
    photos.value[index + 1]?.full_url,
    photos.value[index + 2]?.full_url,
  ]

  for (const url of nearbyUrls) {
    ensureLightboxImagePreloaded(url)
  }
}

// Debounced search watcher
watch(searchInput, (val) => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    activeSearch.value = val.trim()
    currentPage.value = 1
    loadPhotos(1)
  }, 300)
})

// Marquee animation loop
function getOneSetWidth() {
  // Width of one full set of photos inside the track
  if (!marqueeTrack.value || marqueePhotos.value.length === 0) return 0
  const children = marqueeTrack.value.children
  const count = marqueePhotos.value.length
  if (children.length === 0) return 0
  // Each item width + gap (0.75rem = 12px)
  const item = children[0]
  const gap = 12
  return count * (item.offsetWidth + gap)
}

function wrapOffset(offset) {
  const setWidth = getOneSetWidth()
  if (setWidth === 0) return offset
  // Keep offset in the middle set range: [-setWidth, 0]
  // We start at -setWidth (showing the middle copy)
  while (offset > 0) offset -= setWidth
  while (offset < -setWidth) offset += setWidth
  return offset
}

function marqueeLoop() {
  if (!isDragging) {
    if (Math.abs(velocity) > MIN_VELOCITY) {
      // Inertia phase: apply velocity with friction
      marqueeOffset.value += velocity
      velocity *= FRICTION
    } else {
      // Auto-scroll: slow constant drift (pauses on hover)
      velocity = 0
      if (!marqueeHovered.value) {
        marqueeOffset.value -= AUTO_SPEED
      }
    }
  }

  marqueeOffset.value = wrapOffset(marqueeOffset.value)
  rafId = requestAnimationFrame(marqueeLoop)
}

function startMarqueeLoop() {
  // Initialize offset to show the middle (second) copy
  marqueeOffset.value = -getOneSetWidth()
  if (!rafId) rafId = requestAnimationFrame(marqueeLoop)
}

// Drag interaction handlers
function onDragStart(e) {
  isDragging = true
  dragMoved = false
  velocity = 0
  const clientX = e.touches ? e.touches[0].clientX : e.clientX
  dragStartX = clientX
  dragStartOffset = marqueeOffset.value
  lastDragX = clientX
  lastDragTime = performance.now()

  const onMove = (ev) => {
    const cx = ev.touches ? ev.touches[0].clientX : ev.clientX
    const diff = cx - dragStartX
    if (Math.abs(diff) > 5) dragMoved = true
    marqueeOffset.value = wrapOffset(dragStartOffset + diff)

    // Track velocity from recent movement
    const now = performance.now()
    const dt = now - lastDragTime
    if (dt > 0) {
      velocity = (cx - lastDragX) / Math.max(dt, 1) * 16 // normalize to ~60fps
    }
    lastDragX = cx
    lastDragTime = now
  }

  const onEnd = () => {
    isDragging = false
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onEnd)
    window.removeEventListener('touchmove', onMove)
    window.removeEventListener('touchend', onEnd)
    // Clamp inertia velocity to avoid extreme flings
    velocity = Math.max(-15, Math.min(15, velocity))
  }

  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onEnd)
  window.addEventListener('touchmove', onMove, { passive: true })
  window.addEventListener('touchend', onEnd)
}

function onMarqueePhotoClick(photo) {
  if (!dragMoved) {
    openLightbox(photo)
  }
}

function saveName() {
  const name = nameInput.value.trim()
  if (!name) return
  uploaderName.value = name
  localStorage.setItem(STORAGE_KEY, name)
}

function clearName() {
  uploaderName.value = ''
  nameInput.value = ''
  localStorage.removeItem(STORAGE_KEY)
}

function onFilesSelected(event) {
  const files = Array.from(event.target.files || [])
  if (files.length === 0) return
  pendingFiles.value = files
  captionInput.value = ''
  uploadError.value = ''
}

async function startUpload() {
  if (pendingFiles.value.length === 0) return

  isUploading.value = true
  uploadError.value = ''
  uploadTotal.value = pendingFiles.value.length
  uploadCurrent.value = 0

  const caption = captionInput.value.trim() || null
  const filesToUpload = [...pendingFiles.value]
  pendingFiles.value = []

  for (const file of filesToUpload) {
    uploadCurrent.value++
    uploadProgress.value = 0
    try {
      const photo = await uploadPhoto(file, uploaderName.value, caption, (pct) => {
        uploadProgress.value = pct
      })
      // Add to grid if not searching
      if (!activeSearch.value) {
        photos.value.unshift(photo)
      }
      // Always add to marquee cache
      allPhotosCache.value.unshift(photo)
    } catch (err) {
      const msg = err.response?.data?.detail || 'Errore durante il caricamento'
      uploadError.value = msg
    }
  }

  isUploading.value = false
  uploadProgress.value = 0
  captionInput.value = ''
}

async function loadPhotos(page = 1) {
  if (isLoading.value) return
  isLoading.value = true

  try {
    const search = activeSearch.value || null
    const data = await getPhotos(page, PER_PAGE, search)
    if (page === 1) {
      photos.value = data.photos
      // Cache all photos for marquee on initial unfiltered load
      if (!search) {
        allPhotosCache.value = data.photos
      }
    } else {
      photos.value.push(...data.photos)
      // Extend marquee cache on unfiltered pagination
      if (!search) {
        const existingIds = new Set(allPhotosCache.value.map(p => p.id))
        for (const p of data.photos) {
          if (!existingIds.has(p.id)) allPhotosCache.value.push(p)
        }
      }
    }
    currentPage.value = data.page
    totalPages.value = data.total_pages
  } catch {
    // Silently fail on load errors
  } finally {
    isLoading.value = false
  }
}

function loadMore() {
  if (currentPage.value < totalPages.value && !isLoading.value) {
    loadPhotos(currentPage.value + 1)
  }
}

// Lightbox
function openLightbox(photo) {
  lightboxIndex.value = photos.value.indexOf(photo)
  lbTrackOffsetX.value = 0
  lbAnimating.value = false
  lbOverlayOffsetY.value = 0
  lbOverlayAnimating.value = false
  lbTargetIndex = null
  preloadNearbyLightboxPhotos(lightboxIndex.value)
  document.body.style.overflow = 'hidden'
}

function closeLightbox() {
  lightboxIndex.value = -1
  lbTrackOffsetX.value = 0
  lbAnimating.value = false
  lbOverlayOffsetY.value = 0
  lbOverlayAnimating.value = false
  lbTargetIndex = null
  document.body.style.overflow = ''
}

async function sharePhoto() {
  if (!lightboxPhoto.value) return
  const photo = lightboxPhoto.value
  const filename = photo.original_filename || 'photo.jpg'

  try {
    const res = await fetch(photo.full_url)
    const blob = await res.blob()

    // Try native share with file
    if (navigator.share) {
      const file = new File([blob], filename, { type: blob.type })
      if (navigator.canShare?.({ files: [file] })) {
        await navigator.share({ files: [file] })
        return
      }
    }

    // Fallback: download the image
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    // User cancelled or share failed - ignore
  }
}

function setLightboxByIndex(idx) {
  lightboxIndex.value = idx
}

function getLightboxViewportWidth() {
  return lbViewportEl.value?.clientWidth || window.innerWidth
}

function resetLightboxTrack() {
  lbTrackOffsetX.value = 0
  lbTargetIndex = null
}

function animateOverlayBack() {
  if (lbOverlayOffsetY.value === 0) {
    lbOverlayAnimating.value = false
    return
  }

  lbOverlayAnimating.value = true
  lbOverlayOffsetY.value = 0
  window.setTimeout(() => {
    lbOverlayAnimating.value = false
  }, 220)
}

function dismissLightboxWithGesture() {
  const height = lbViewportEl.value?.clientHeight || window.innerHeight || 1
  const direction = lbTouchDeltaY >= 0 ? 1 : -1

  lbOverlayAnimating.value = true
  lbOverlayOffsetY.value = direction * Math.min(height * 0.32, 220)

  window.setTimeout(() => {
    closeLightbox()
  }, 220)
}

function getLightboxTargetIndex(dir) {
  const targetIndex = lightboxIndex.value + dir
  if (targetIndex < 0 || targetIndex >= photos.value.length) return null
  return targetIndex
}

function animateTrackTo(offset, targetIndex = null) {
  lbTargetIndex = targetIndex
  lbAnimating.value = true
  lbTrackOffsetX.value = offset
}

function onLightboxTrackTransitionEnd() {
  if (!lbAnimating.value) return

  lbAnimating.value = false
  if (lbTargetIndex !== null) {
    setLightboxByIndex(lbTargetIndex)
  }
  resetLightboxTrack()
}

function slideToPhoto(dir) {
  if (lbAnimating.value || lbOverlayAnimating.value || lbOverlayOffsetY.value !== 0 || !lightboxPhoto.value) return
  const targetIndex = getLightboxTargetIndex(dir)
  if (targetIndex === null) {
    if (lbTrackOffsetX.value !== 0) {
      animateTrackTo(0)
    }
    return
  }

  preloadNearbyLightboxPhotos(targetIndex)
  animateTrackTo(-dir * getLightboxViewportWidth(), targetIndex)
}

function updateLightboxDrag(dx) {
  const atStart = lightboxIndex.value === 0 && dx > 0
  const atEnd = lightboxIndex.value === photos.value.length - 1 && dx < 0
  lbTargetIndex = null
  lbTrackOffsetX.value = (atStart || atEnd) ? dx * 0.3 : dx
}

function finishCancelledDrag() {
  if (lbTrackOffsetX.value === 0) {
    resetLightboxTrack()
    return
  }
  animateTrackTo(0)
}

function onKeydown(e) {
  if (!lightboxPhoto.value) return
  if (e.key === 'Escape') closeLightbox()
  if (e.key === 'ArrowLeft') slideToPhoto(-1)
  if (e.key === 'ArrowRight') slideToPhoto(1)
}

function onLbTouchStart(e) {
  if (lbAnimating.value || lbOverlayAnimating.value) return
  lbTouchStartX = e.touches[0].clientX
  lbTouchStartY = e.touches[0].clientY
  lbTouchDeltaX = 0
  lbTouchDeltaY = 0
  lbGestureAxis = null
}

function onLbTouchMove(e) {
  if (lbAnimating.value || lbOverlayAnimating.value) return
  const dx = e.touches[0].clientX - lbTouchStartX
  const dy = e.touches[0].clientY - lbTouchStartY

  if (!lbGestureAxis) {
    if (Math.abs(dy) > Math.abs(dx) && Math.abs(dy) > 10) {
      lbGestureAxis = 'y'
    } else if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 10) {
      lbGestureAxis = 'x'
    }
  }

  if (lbGestureAxis === 'y') {
    lbTouchDeltaY = dy
    lbOverlayOffsetY.value = dy
    return
  }

  if (lbGestureAxis === 'x') {
    lbTouchDeltaX = dx
    updateLightboxDrag(dx)
  }
}

function onLbTouchEnd() {
  if (lbAnimating.value || lbOverlayAnimating.value) return

  if (lbGestureAxis === 'y') {
    const dismissThreshold = Math.min((lbViewportEl.value?.clientHeight || window.innerHeight) * 0.16, 140)
    if (Math.abs(lbTouchDeltaY) > dismissThreshold) {
      dismissLightboxWithGesture()
    } else {
      animateOverlayBack()
    }
    lbTouchDeltaX = 0
    lbTouchDeltaY = 0
    lbGestureAxis = null
    return
  }

  const threshold = getLightboxViewportWidth() * 0.2
  if (lbTouchDeltaX > threshold) {
    slideToPhoto(-1)
  } else if (lbTouchDeltaX < -threshold) {
    slideToPhoto(1)
  } else {
    finishCancelledDrag()
  }
  lbTouchDeltaX = 0
  lbTouchDeltaY = 0
  lbGestureAxis = null
}

function onLbTouchCancel() {
  if (lbAnimating.value || lbOverlayAnimating.value) return
  if (lbGestureAxis === 'y') {
    animateOverlayBack()
  } else {
    finishCancelledDrag()
  }
  lbTouchDeltaX = 0
  lbTouchDeltaY = 0
  lbGestureAxis = null
}

// IntersectionObserver for infinite scroll
let observer = null

onMounted(() => {
  loadPhotos(1)
  window.addEventListener('keydown', onKeydown)

  nextTick(() => {
    if (sentinel.value) {
      observer = new IntersectionObserver(
        (entries) => {
          if (entries[0].isIntersecting) loadMore()
        },
        { rootMargin: '200px' }
      )
      observer.observe(sentinel.value)
    }
  })
})

// Start marquee loop once photos are loaded into the cache
watch(marqueePhotos, (val) => {
  if (val.length > 0) {
    nextTick(() => startMarqueeLoop())
  }
})

watch(lightboxIndex, (idx) => {
  if (idx >= 0) {
    preloadNearbyLightboxPhotos(idx)
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  if (observer) observer.disconnect()
  if (debounceTimer) clearTimeout(debounceTimer)
  if (rafId) cancelAnimationFrame(rafId)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.marquee-wrapper {
  margin-left: -0.5rem;
  margin-right: -0.5rem;
}

.marquee-container {
  overflow: hidden;
  -webkit-mask-image: linear-gradient(
    to right,
    transparent 0%,
    black 6%,
    black 94%,
    transparent 100%
  );
  mask-image: linear-gradient(
    to right,
    transparent 0%,
    black 6%,
    black 94%,
    transparent 100%
  );
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
}

.marquee-container:active {
  cursor: grabbing;
}

.marquee-track {
  will-change: transform;
}

/* Lightbox swipe */
.lightbox-overlay {
  touch-action: none;
  overscroll-behavior: contain;
}

.lightbox-media-animating {
  transition: transform 0.22s ease, border-radius 0.22s ease;
}

.lightbox-track {
  display: flex;
  will-change: transform;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  transform-style: preserve-3d;
}

.lightbox-slide {
  flex: 0 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

.lightbox-animating {
  transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.lightbox-slide img {
  transform: translateZ(0);
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

</style>
