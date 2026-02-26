<template>
  <div
    class="card transition-all hover:shadow-lg overflow-x-hidden overflow-y-scroll overscroll-contain touch-pan-y max-h-[82svh] pointer-events-auto scroll-pb-24 [-webkit-overflow-scrolling:touch]"
    :class="[
      hasAnyAttendingDraft && !submissionFeedback ? 'bg-[#eef5e6] ring-2 ring-forest/45 shadow-[0_0_0_3px_rgba(61,79,61,0.18),0_0_24px_rgba(157,173,143,0.38)]' : '',
      submissionFeedback ? 'rsvp-submit-bump bg-[#eef5e6] ring-2 ring-forest/45 shadow-[0_0_0_3px_rgba(61,79,61,0.24),0_0_34px_rgba(157,173,143,0.62)]' : ''
    ]"
    @touchmove.stop
    @wheel.stop
  >
    <div v-if="submissionFeedback" class="py-6 px-3 text-center">
      <p class="font-serif text-forest text-lg leading-[1.35]">
        {{ submissionFeedback }}
      </p>
    </div>

    <div v-else class="space-y-4">
      <div v-if="!activeGuest" class="space-y-4">
        <div class="flex items-center justify-between gap-3">
          <h3 v-if="showTitle" class="font-serif text-forest text-lg font-medium">
            {{ family.family_name }}
          </h3>
          <button
            type="button"
            aria-label="Chiudi"
            class="inline-flex items-center justify-center w-9 h-9 rounded-full border-2 border-forest/25 text-forest/80 hover:text-forest hover:border-forest/45 hover:bg-forest/5 transition-colors"
            :disabled="saving"
            @click="requestClose"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M6 6l12 12M18 6 6 18" />
            </svg>
          </button>
        </div>

        <div class="rounded-2xl border border-forest/15 bg-cream/60 p-3">
          <p class="font-serif text-sm text-forest/80 mb-2">
            Seleziona un componente da modificare
          </p>
          <div class="space-y-1.5">
            <button
              v-for="guest in family.guests"
              :key="guest.id"
              type="button"
              class="w-full text-left rounded-xl border border-forest/15 bg-cream/70 px-3 py-2.5 transition-colors hover:bg-cream"
              :disabled="saving"
              @click="openGuestEditor(guest)"
            >
              <div class="flex items-center justify-between gap-3">
                <div class="min-w-0 flex items-center gap-2 text-left">
                  <span class="font-serif text-forest text-base leading-tight truncate">
                    {{ guest.name }}
                  </span>
                  <span class="font-serif text-xs text-forest/65 leading-tight whitespace-nowrap">
                    ({{ memberInlineStatusLabel(guest) }})
                  </span>
                  <span
                    v-if="isGuestDirty(guest) && memberDraftOutcomeLabel(guest)"
                    class="font-serif text-xs text-forest/70 leading-tight whitespace-nowrap"
                  >
                    ({{ memberDraftOutcomeLabel(guest) }})
                  </span>
                </div>
                <div class="flex items-center gap-2 shrink-0">
                  <span
                    class="w-2 h-2 rounded-full"
                    :class="memberMarkerClass(guest)"
                    aria-hidden="true"
                  />
                  <svg class="w-4 h-4 text-forest/60" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="m9 6 6 6-6 6" />
                  </svg>
                </div>
              </div>
            </button>
          </div>
          <p class="mt-1.5 font-serif text-xs text-forest/65 leading-tight">
            Le modifiche restano in bozza finché non salvi la famiglia.
          </p>
        </div>

        <div class="pt-2 border-t border-forest/10 bg-cream">
          <div class="rounded-2xl border-2 border-forest/20 bg-[#f6f1e7] p-3 shadow-[0_8px_18px_rgba(20,35,20,0.06)]">
            <p class="font-serif text-xs text-forest/70">
              Clicca qui per salvare le modifiche.
            </p>
            <p v-if="saveError" class="mb-2 text-sm text-red-800 font-serif mt-2">{{ saveError }}</p>
            <div class="grid grid-cols-2 gap-2 mt-2">
              <button
                type="button"
                class="font-serif leading-[1.05] px-3 py-2.5 rounded-xl border-2 transition-colors text-base sm:text-lg"
                :class="isDirty ? 'bg-forest text-cream border-forest hover:opacity-95' : 'bg-forest/10 text-forest/55 border-forest/25'"
                :disabled="saving || !isDirty"
                @click="saveFamilyDraft"
              >
                Salva famiglia
              </button>
              <button
                type="button"
                class="font-serif leading-[1.05] px-3 py-2.5 rounded-xl border-2 bg-cream text-forest border-forest/25 hover:bg-forest/5 transition-colors text-base sm:text-lg"
                :disabled="saving || !isDirty"
                @click="resetFamilyDraft"
              >
                Annulla
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="space-y-4 pb-2">
        <div class="flex items-center justify-between gap-2">
          <button
            type="button"
            class="inline-flex items-center gap-2 px-3 py-2 rounded-xl border-2 border-forest/25 text-forest hover:bg-forest/5 hover:border-forest/40 transition-colors font-serif text-sm"
            :disabled="saving"
            @click="goBackToFamily"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="m15 18-6-6 6-6" />
            </svg>
            Indietro
          </button>
          <button
            type="button"
            aria-label="Chiudi"
            class="inline-flex items-center justify-center w-9 h-9 rounded-full border-2 border-forest/25 text-forest/80 hover:text-forest hover:border-forest/45 hover:bg-forest/5 transition-colors"
            :disabled="saving"
            @click="requestClose"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M6 6l12 12M18 6 6 18" />
            </svg>
          </button>
        </div>

        <div class="rounded-2xl border border-forest/15 bg-cream/60 p-3 space-y-4">
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="font-serif text-forest text-lg">{{ activeGuest.name }}</p>
              <p class="font-serif text-xs text-forest/70 mt-1">
                {{ activeGuestStatusLabel }}
                <span v-if="isGuestDirty(activeGuest)"> · Modifiche non salvate</span>
              </p>
              <p class="font-serif text-xs text-forest/60 mt-1">
                Torna alla famiglia per salvare tutte le bozze insieme.
              </p>
            </div>
            <span v-if="saving" class="text-xs font-serif text-forest/70 whitespace-nowrap">Salvataggio...</span>
          </div>

          <div class="space-y-2 rounded-2xl border border-forest/15 bg-cream/60 p-3">
            <button
              type="button"
              class="w-full text-left font-serif leading-[1.3] px-4 py-3.5 rounded-xl border-2 transition-colors"
              :class="activeOverallChoice === 'attend' ? 'bg-forest text-cream border-forest' : 'bg-forest/10 text-forest border-forest/40 hover:bg-forest/15'"
              :disabled="saving"
              @click="selectGuestAttending(activeGuest)"
            >
              Ci sarò
            </button>
            <button
              type="button"
              class="w-full text-left font-serif leading-[1.3] px-4 py-3.5 rounded-xl border-2 transition-colors"
              :class="activeOverallChoice === 'decline' ? 'bg-forest text-cream border-forest' : 'bg-forest/10 text-forest border-forest/40 hover:bg-forest/15'"
              :disabled="saving"
              @click="selectGuestDecline(activeGuest)"
            >
              Non ci sarò
            </button>
          </div>

          <div v-if="showActiveEventDetails" class="space-y-3 pt-1">
            <div
              v-for="eventOption in RSVP_EVENT_OPTIONS"
              :key="`${activeGuest.id}-${eventOption.key}`"
              class="rounded-xl border border-forest/15 bg-cream/70 p-3"
            >
              <div class="flex items-center justify-between gap-2">
                <span class="font-serif text-forest text-sm">{{ eventOption.label }}</span>
                <div class="flex items-center gap-2">
                  <button
                    type="button"
                    class="font-serif leading-[1.25] px-3 py-2 rounded-full border-2 transition-colors text-sm"
                    :class="attendanceStateFor(activeGuest)[eventOption.key] === true ? 'bg-forest text-cream border-forest' : 'bg-forest/10 text-forest border-forest/40 hover:bg-forest/15'"
                    :disabled="saving"
                    @click="setGuestEventAttendance(activeGuest, eventOption.key, true)"
                  >
                    Si
                  </button>
                  <button
                    type="button"
                    class="font-serif leading-[1.25] px-3 py-2 rounded-full border-2 transition-colors text-sm"
                    :class="attendanceStateFor(activeGuest)[eventOption.key] === false ? 'bg-forest text-cream border-forest' : 'bg-forest/10 text-forest border-forest/40 hover:bg-forest/15'"
                    :disabled="saving"
                    @click="setGuestEventAttendance(activeGuest, eventOption.key, false)"
                  >
                    No
                  </button>
                </div>
              </div>
            </div>

            <div class="pb-1 rounded-xl border border-forest/15 bg-cream/60 overflow-hidden">
              <button
                type="button"
                class="w-full p-3 text-left transition-colors hover:bg-cream/80"
                :disabled="saving"
                @click="toggleAllergensAccordion"
              >
                <div class="flex items-center justify-between gap-3">
                  <div>
                    <p class="font-serif text-sm text-forest">Allergeni e Intolleranze</p>
                    <p class="font-serif text-xs text-forest/70 leading-[1.2] mt-1">
                      {{ activeAllergensSummaryText }}
                    </p>
                  </div>
                  <div class="flex items-center gap-2">
                    <span
                      class="font-serif text-xs px-2 py-1 rounded-full border"
                      :class="activeAllergenCount > 0 ? 'border-forest/35 text-forest bg-forest/5' : 'border-forest/20 text-forest/60 bg-transparent'"
                    >
                      {{ activeAllergenCount }}
                    </span>
                    <svg
                      class="w-4 h-4 text-forest/70 transition-transform"
                      :class="allergensOpen ? 'rotate-180' : ''"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="m6 9 6 6 6-6" />
                    </svg>
                  </div>
                </div>
              </button>

              <Transition name="fade">
                <div v-if="allergensOpen" class="border-t border-forest/10 bg-cream/70 p-3">
                  <p class="font-serif text-xs text-forest/70 mb-2">
                    Tocca per selezionare uno o più allergeni
                  </p>
                  <div class="grid grid-cols-2 gap-2">
                    <button
                      v-for="option in ALLERGEN_OPTIONS"
                      :key="`${activeGuest.id}-${option.value}`"
                      type="button"
                      class="min-h-[2.5rem] font-serif text-sm leading-[1.2] px-3 py-2 rounded-xl border transition-colors text-left"
                      :class="guestAllergens(activeGuest).includes(option.value) ? 'bg-forest text-cream border-forest' : 'bg-cream text-forest border-forest/25 hover:bg-forest/10'"
                      :disabled="saving"
                      @click="toggleGuestAllergen(activeGuest, option.value)"
                    >
                      {{ option.label }}
                    </button>
                  </div>
                </div>
              </Transition>
            </div>
          </div>

          <div class="pt-1 border-t border-forest/10">
            <button
              type="button"
              class="w-full font-serif text-center leading-[1.1] px-3 py-2 rounded-xl border bg-[#f6f1e7] text-forest/90 border-forest/20 hover:bg-forest/5 transition-colors text-sm"
              :disabled="saving"
              @click="applyActiveDraftToAllMembers"
            >
              Applica a tutti i membri
            </button>
          </div>
        </div>

        <div class="rounded-xl border border-forest/15 bg-cream/60 p-3">
          <p class="font-serif text-xs text-forest/70">
            {{ isDirty ? `Bozze famiglia pronte da salvare: ${dirtyGuestCount}` : 'Nessuna bozza in attesa di salvataggio' }}
          </p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { updateGuest } from '../services/api'
import { ALLERGEN_OPTIONS, RSVP_EVENT_OPTIONS, getGuestAttendanceState, isDeclinedState } from '../constants/rsvp'

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

const emit = defineEmits(['updated', 'close', 'saved'])

const selectedGuestId = ref(null)
const allergensOpen = ref(false)
const saving = ref(false)
const saveError = ref('')
const submissionFeedback = ref('')
const drafts = reactive({})
const baselines = reactive({})
const forceShowEventDetailsByGuestId = reactive({})
let completionTimerId = null

const allergenLabelsByValue = computed(() => new Map(ALLERGEN_OPTIONS.map(option => [option.value, option.label])))

function snapshotFromGuest(guest) {
  const state = getGuestAttendanceState(guest)
  const allergens = Array.isArray(guest?.allergens) ? [...guest.allergens] : []
  return {
    attend_ceremony: state.attend_ceremony,
    attend_lunch: state.attend_lunch,
    allergens
  }
}

function normalizedSnapshot(snapshot) {
  return JSON.stringify({
    attend_ceremony: snapshot.attend_ceremony,
    attend_lunch: snapshot.attend_lunch,
    allergens: [...snapshot.allergens].sort()
  })
}

function ensureGuestBuffers(guest) {
  if (!drafts[guest.id]) {
    const snap = snapshotFromGuest(guest)
    drafts[guest.id] = { ...snap, allergens: [...snap.allergens] }
    baselines[guest.id] = { ...snap, allergens: [...snap.allergens] }
    forceShowEventDetailsByGuestId[guest.id] = snap.attend_ceremony === true || snap.attend_lunch === true
  }
}

function assignSnapshot(target, snapshot) {
  target.attend_ceremony = snapshot.attend_ceremony
  target.attend_lunch = snapshot.attend_lunch
  target.allergens = [...snapshot.allergens]
}

function snapshotFromDraft(guest) {
  const draft = draftFor(guest)
  return {
    attend_ceremony: draft.attend_ceremony,
    attend_lunch: draft.attend_lunch,
    allergens: [...draft.allergens]
  }
}

function isGuestDirtyById(guestId) {
  return normalizedSnapshot(drafts[guestId]) !== normalizedSnapshot(baselines[guestId])
}

function syncGuestFromProps(guest) {
  ensureGuestBuffers(guest)
  const incoming = snapshotFromGuest(guest)
  const wasDirty = isGuestDirtyById(guest.id)
  const baselineChanged = normalizedSnapshot(incoming) !== normalizedSnapshot(baselines[guest.id])
  if (!baselineChanged) return

  assignSnapshot(baselines[guest.id], incoming)
  if (!wasDirty) {
    assignSnapshot(drafts[guest.id], incoming)
    forceShowEventDetailsByGuestId[guest.id] = incoming.attend_ceremony === true || incoming.attend_lunch === true
  }
}

watch(
  () => props.family.guests,
  (guests = []) => {
    for (const guest of guests) syncGuestFromProps(guest)

    const ids = new Set(guests.map(guest => guest.id))
    if (selectedGuestId.value && !ids.has(selectedGuestId.value)) {
      selectedGuestId.value = null
      allergensOpen.value = false
    }
  },
  { immediate: true, deep: true }
)

const activeGuest = computed(() => (
  props.family.guests.find(guest => guest.id === selectedGuestId.value) || null
))

const isDirty = computed(() => props.family.guests.some(guest => {
  ensureGuestBuffers(guest)
  return isGuestDirtyById(guest.id)
}))

const dirtyGuestCount = computed(() => props.family.guests.reduce((count, guest) => (
  count + (isGuestDirty(guest) ? 1 : 0)
), 0))

const hasAnyAttendingDraft = computed(() => props.family.guests.some(guest => {
  ensureGuestBuffers(guest)
  const state = attendanceStateFor(guest)
  return state.attend_ceremony === true || state.attend_lunch === true
}))

const activeOverallChoice = computed(() => (
  activeGuest.value ? overallChoiceForGuest(activeGuest.value) : null
))

const showActiveEventDetails = computed(() => {
  if (!activeGuest.value) return false
  return Boolean(forceShowEventDetailsByGuestId[activeGuest.value.id]) || activeOverallChoice.value === 'attend'
})

const activeAllergenCount = computed(() => (
  activeGuest.value ? guestAllergens(activeGuest.value).length : 0
))

const activeAllergensSummaryText = computed(() => {
  if (!activeGuest.value) return 'Nessuno selezionato'
  const allergens = guestAllergens(activeGuest.value)
  if (allergens.length === 0) return 'Nessuno selezionato'
  if (allergens.length <= 2) return allergens.map(value => allergenLabelsByValue.value.get(value) || value).join(', ')
  return `${allergens.length} selezionati`
})

const activeGuestStatusLabel = computed(() => (
  activeGuest.value ? guestStatusLabel(activeGuest.value) : ''
))

function draftFor(guest) {
  ensureGuestBuffers(guest)
  return drafts[guest.id]
}

function baselineFor(guest) {
  ensureGuestBuffers(guest)
  return baselines[guest.id]
}

function attendanceStateFor(guest) {
  const draft = draftFor(guest)
  return {
    attend_ceremony: draft.attend_ceremony,
    attend_lunch: draft.attend_lunch
  }
}

function guestAllergens(guest) {
  return draftFor(guest).allergens
}

function overallChoiceForGuest(guest) {
  const state = attendanceStateFor(guest)
  if (state.attend_ceremony === false && state.attend_lunch === false) return 'decline'
  if (state.attend_ceremony === true || state.attend_lunch === true) return 'attend'
  return null
}

function guestStatusLabel(guest) {
  const state = attendanceStateFor(guest)
  if (isDeclinedState(state)) return 'Non ci sarà'
  if (state.attend_ceremony === true || state.attend_lunch === true) return 'Ci sarà'
  return 'Da confermare'
}

function memberMarkerClass(guest) {
  if (isGuestDirty(guest)) return 'bg-amber-500'
  const state = attendanceStateFor(guest)
  if (isDeclinedState(state)) return 'bg-forest/40'
  if (state.attend_ceremony === true || state.attend_lunch === true) return 'bg-forest'
  return 'bg-forest/20'
}

function memberPillClass(guest) {
  const selected = selectedGuestId.value === guest.id
  const dirty = isGuestDirty(guest)
  if (selected && dirty) return 'bg-[#eef5e6] text-forest border-forest shadow-sm'
  if (selected) return 'bg-forest text-cream border-forest'
  if (dirty) return 'bg-[#f6f1e7] text-forest border-forest/45'
  return 'bg-cream text-forest border-forest/25 hover:bg-forest/5'
}

function memberInlineStatusLabel(guest) {
  if (isGuestDirty(guest)) return 'Bozza'
  const state = attendanceStateFor(guest)
  if (isDeclinedState(state)) return 'Non ci sara'
  if (state.attend_ceremony === true || state.attend_lunch === true) return 'Ci sara'
  return 'Da confermare'
}

function memberDraftOutcomeLabel(guest) {
  if (!isGuestDirty(guest)) return ''
  const state = attendanceStateFor(guest)
  if (isDeclinedState(state)) return 'Non ci sara'
  if (state.attend_ceremony === true || state.attend_lunch === true) return 'Ci sara'
  return 'Da confermare'
}

function isGuestDirty(guest) {
  ensureGuestBuffers(guest)
  return isGuestDirtyById(guest.id)
}

function selectGuest(guest) {
  if (saving.value) return
  if (selectedGuestId.value === guest.id) return
  selectedGuestId.value = guest.id
  allergensOpen.value = false
}

function openGuestEditor(guest) {
  selectGuest(guest)
}

function goBackToFamily() {
  if (saving.value) return
  selectedGuestId.value = null
  allergensOpen.value = false
}

function selectGuestAttending(guest) {
  if (saving.value) return
  const draft = draftFor(guest)
  draft.attend_ceremony = true
  draft.attend_lunch = true
  forceShowEventDetailsByGuestId[guest.id] = true
  saveError.value = ''
}

function selectGuestDecline(guest) {
  if (saving.value) return
  const draft = draftFor(guest)
  draft.attend_ceremony = false
  draft.attend_lunch = false
  forceShowEventDetailsByGuestId[guest.id] = false
  if (selectedGuestId.value === guest.id) allergensOpen.value = false
  saveError.value = ''
}

function setGuestEventAttendance(guest, field, value) {
  if (saving.value) return
  const draft = draftFor(guest)
  draft[field] = value
  if (value === true) {
    forceShowEventDetailsByGuestId[guest.id] = true
  } else if (draft.attend_ceremony === false && draft.attend_lunch === false) {
    forceShowEventDetailsByGuestId[guest.id] = false
    if (selectedGuestId.value === guest.id) allergensOpen.value = false
  }
  saveError.value = ''
}

function toggleAllergensAccordion() {
  if (saving.value || !activeGuest.value) return
  allergensOpen.value = !allergensOpen.value
}

function toggleGuestAllergen(guest, allergen) {
  if (saving.value) return
  if (isDeclinedState(attendanceStateFor(guest))) return
  const draft = draftFor(guest)
  if (draft.allergens.includes(allergen)) {
    draft.allergens = draft.allergens.filter(item => item !== allergen)
  } else {
    draft.allergens = [...draft.allergens, allergen]
  }
  saveError.value = ''
}

function applyActiveDraftToAllMembers() {
  if (saving.value || !activeGuest.value) return

  const sourceGuest = activeGuest.value
  const sourceSnapshot = snapshotFromDraft(sourceGuest)
  const showDetails = sourceSnapshot.attend_ceremony === true || sourceSnapshot.attend_lunch === true

  for (const guest of props.family.guests) {
    ensureGuestBuffers(guest)
    assignSnapshot(drafts[guest.id], sourceSnapshot)
    forceShowEventDetailsByGuestId[guest.id] = showDetails
  }

  if (!showDetails) {
    allergensOpen.value = false
  }
  saveError.value = ''
  goBackToFamily()
}

function resetFamilyDraft() {
  for (const guest of props.family.guests) {
    ensureGuestBuffers(guest)
    assignSnapshot(drafts[guest.id], baselines[guest.id])
    forceShowEventDetailsByGuestId[guest.id] = (
      baselines[guest.id].attend_ceremony === true || baselines[guest.id].attend_lunch === true
    )
  }
  allergensOpen.value = false
  saveError.value = ''
}

function clearCompletionTimer() {
  if (completionTimerId) {
    clearTimeout(completionTimerId)
    completionTimerId = null
  }
}

function confirmIfNeeded() {
  if (sessionStorage.getItem('rsvp_updated') === 'pending') {
    if (!window.confirm('Stai modificando le partecipazioni della famiglia.\nClicca OK per procedere comunque.')) return false
    sessionStorage.setItem('rsvp_updated', 'confirmed')
  }
  return true
}

function requestClose() {
  if (saving.value) return
  if (isDirty.value) {
    const ok = window.confirm('Hai modifiche non salvate nella famiglia. Vuoi chiudere senza salvare?')
    if (!ok) return
  }
  clearCompletionTimer()
  submissionFeedback.value = ''
  emit('close')
}

function familyWarningMessage(warning) {
  if (!warning) return ''
  if (warning.includes('comunicaci solo la tua partecipazione')) {
    return warning
      .replace('comunicaci', 'comunicateci')
      .replace('la tua partecipazione', 'le vostre partecipazioni')
  }
  return warning
}

async function saveFamilyDraft() {
  if (saving.value || !isDirty.value) return
  if (!confirmIfNeeded()) return

  saving.value = true
  saveError.value = ''

  const dirtyGuests = props.family.guests.filter(guest => isGuestDirty(guest))
  const failedGuestNames = []
  const updatedGuests = []
  let batchWarning = ''

  try {
    for (const guest of dirtyGuests) {
      const draft = draftFor(guest)
      try {
        const result = await updateGuest(
          guest.id,
          {
            attend_ceremony: draft.attend_ceremony,
            attend_lunch: draft.attend_lunch,
            allergens: [...draft.allergens]
          },
          { suppressWarningAlert: true, returnMeta: true }
        )
        const updated = result.data
        if (!batchWarning && result.warning) batchWarning = result.warning
        updatedGuests.push(updated)
        if (!sessionStorage.getItem('rsvp_updated')) sessionStorage.setItem('rsvp_updated', 'pending')

        const snap = snapshotFromGuest(updated)
        assignSnapshot(baselines[guest.id], snap)
        assignSnapshot(drafts[guest.id], snap)
        forceShowEventDetailsByGuestId[guest.id] = snap.attend_ceremony === true || snap.attend_lunch === true

        emit('updated', { guestId: guest.id, guest: updated })
      } catch (error) {
        failedGuestNames.push(guest.name)
        console.error(`Failed to save family guest RSVP (${guest.name}):`, error)
      }
    }

    if (failedGuestNames.length > 0) {
      if (updatedGuests.length > 0) {
        saveError.value = `Alcune risposte sono state salvate, ma non tutte (${failedGuestNames.join(', ')}). Riprova.`
      } else {
        saveError.value = 'Errore nel salvataggio. Riprova.'
      }
      return
    }

    const anyPresence = props.family.guests.some(guest => {
      const state = attendanceStateFor(guest)
      return state.attend_ceremony === true || state.attend_lunch === true
    })
    saveError.value = ''
    submissionFeedback.value = anyPresence
      ? 'Grazie per la vostra presenza, ci vediamo presto per festeggiare insieme'
      : 'Ci dispiace che non potrete esserci, ci saranno altre occasioni per celebrare insieme'

    if (batchWarning) {
      window.alert(familyWarningMessage(batchWarning))
    }
    emit('saved')

    clearCompletionTimer()
    completionTimerId = setTimeout(() => {
      emit('close')
    }, 1400)
  } finally {
    saving.value = false
  }
}

onBeforeUnmount(() => {
  clearCompletionTimer()
})
</script>

<style scoped>
.rsvp-submit-bump {
  animation: rsvp-submit-bump 0.42s cubic-bezier(0.2, 0.8, 0.2, 1);
}

@keyframes rsvp-submit-bump {
  0% { transform: scale(0.97); opacity: 0.88; }
  60% { transform: scale(1.02); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}
</style>
