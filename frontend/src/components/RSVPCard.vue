<template>
  <div
    class="card-individual transition-all hover:shadow-lg overflow-hidden"
    :class="[
      draftOverallChoice === 'attend' && !submissionFeedback ? 'bg-[#eef5e6] ring-2 ring-forest/45 shadow-[0_0_0_3px_rgba(61,79,61,0.24),0_0_34px_rgba(157,173,143,0.62)]' : '',
      submissionFeedback ? 'rsvp-submit-bump bg-[#eef5e6] ring-2 ring-forest/45 shadow-[0_0_0_3px_rgba(61,79,61,0.24),0_0_34px_rgba(157,173,143,0.62)]' : ''
    ]"
  >
    <div v-if="submissionFeedback" class="py-6 px-2 text-center">
      <p class="font-serif text-forest text-lg leading-[1.35]">
        {{ submissionFeedback }}
      </p>
    </div>

    <div v-else class="space-y-4">
      <div class="flex items-start justify-between gap-4">
        <span class="font-serif text-forest text-lg">{{ guest.name }}</span>
        <div class="flex items-center gap-2">
          <span v-if="saving" class="text-xs font-serif text-forest/70">Salvataggio...</span>
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
      </div>

      <div class="space-y-4">
        <div class="space-y-2 rounded-2xl border border-forest/15 bg-cream/60 p-3">
          <button
            type="button"
            class="w-full text-left font-serif leading-[1.3] px-4 py-3.5 rounded-xl border-2 transition-colors overflow-visible"
            :class="draftOverallChoice === 'attend' ? 'bg-forest text-cream border-forest' : 'bg-forest/10 text-forest border-forest/40 hover:bg-forest/15'"
            :disabled="saving"
            @click="selectAttending"
          >
            Ci sarò
          </button>
          <button
            type="button"
            class="w-full text-left font-serif leading-[1.3] px-4 py-3.5 rounded-xl border-2 transition-colors overflow-visible"
            :class="draftOverallChoice === 'decline' ? 'bg-forest text-cream border-forest' : 'bg-forest/10 text-forest border-forest/40 hover:bg-forest/15'"
            :disabled="saving"
            @click="selectDecline"
          >
            Non ci sarò
          </button>
        </div>

        <div v-if="showEventDetails" class="space-y-3 pt-1">
          <div
            v-for="eventOption in RSVP_EVENT_OPTIONS"
            :key="eventOption.key"
            class="rounded-xl border border-forest/15 bg-cream/60 p-3"
          >
            <div class="flex items-center justify-between gap-3">
              <span class="font-serif text-forest">{{ eventOption.label }}</span>
              <div class="flex items-center gap-2">
                <button
                  type="button"
                  class="font-serif leading-[1.25] px-3 py-2 rounded-full border-2 transition-colors text-sm overflow-visible"
                  :class="draft[eventOption.key] === true ? 'bg-forest text-cream border-forest' : 'bg-forest/10 text-forest border-forest/40 hover:bg-forest/15'"
                  :disabled="saving"
                  @click="setEventAttendance(eventOption.key, true)"
                >
                  Si
                </button>
                <button
                  type="button"
                  class="font-serif leading-[1.25] px-3 py-2 rounded-full border-2 transition-colors text-sm overflow-visible"
                  :class="draft[eventOption.key] === false ? 'bg-forest text-cream border-forest' : 'bg-forest/10 text-forest border-forest/40 hover:bg-forest/15'"
                  :disabled="saving"
                  @click="setEventAttendance(eventOption.key, false)"
                >
                  No
                </button>
              </div>
            </div>
          </div>

          <div
            class="pb-1 rounded-xl border border-forest/15 bg-cream/60 overflow-hidden"
            :class="allergensOpen ? 'shadow-[inset_0_1px_0_rgba(255,255,255,0.35)]' : ''"
          >
            <button
              type="button"
              ref="allergensToggleButton"
              class="w-full p-3 text-left transition-colors hover:bg-cream/80"
              :disabled="saving"
              @click="toggleAllergensAccordion"
            >
              <div class="flex items-center justify-between gap-3">
                <div>
                  <p class="font-serif text-sm text-forest">Allergeni e Intolleranze</p>
                  <p class="font-serif text-xs text-forest/70 leading-[1.2] mt-1">
                    {{ allergensSummaryText }}
                  </p>
                </div>
                <div class="flex items-center gap-2">
                  <span
                    class="font-serif text-xs px-2 py-1 rounded-full border"
                    :class="selectedAllergenCount > 0 ? 'border-forest/35 text-forest bg-forest/5' : 'border-forest/20 text-forest/60 bg-transparent'"
                  >
                    {{ selectedAllergenCount }}
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
              <div
                v-if="allergensOpen"
                ref="allergensPanel"
                class="border-t border-forest/10 bg-cream/70 p-3"
                :class="{ 'allergens-panel-flash': allergensJustOpened }"
              >
                <div class="mb-2">
                  <p class="font-serif text-xs text-forest/70">
                    Tocca per selezionare uno o più allergeni
                  </p>
                </div>

                <div class="grid grid-cols-2 gap-2">
                  <button
                    v-for="option in ALLERGEN_OPTIONS"
                    :key="option.value"
                    type="button"
                    class="min-h-[2.5rem] font-serif text-sm leading-[1.2] px-3 py-2 rounded-xl border transition-colors text-left"
                    :class="draft.allergens.includes(option.value) ? 'bg-forest text-cream border-forest' : 'bg-cream text-forest border-forest/25 hover:bg-forest/10'"
                    :disabled="saving"
                    @click="toggleAllergen(option.value)"
                  >
                    {{ option.label }}
                  </button>
                </div>

              </div>
            </Transition>
          </div>
        </div>
      </div>

      <div class="pt-3 border-t border-forest/10 bg-cream">
        <p v-if="saveError" class="mb-2 text-sm text-red-800 font-serif">{{ saveError }}</p>
        <p v-else-if="isDirty" class="mb-2 text-xs text-forest/65 font-serif">Modifiche non salvate</p>
        <div class="flex gap-2">
          <button
            type="button"
            class="flex-1 font-serif leading-[1.25] px-4 py-3 rounded-xl border-2 transition-colors"
            :class="isDirty ? 'bg-forest text-cream border-forest hover:opacity-95' : 'bg-forest/10 text-forest/55 border-forest/25'"
            :disabled="saving || !isDirty"
            @click="saveDraft"
          >
            Salva risposta
          </button>
          <button
            v-if="isDirty"
            type="button"
            class="font-serif leading-[1.25] px-4 py-3 rounded-xl border-2 bg-cream text-forest border-forest/25 hover:bg-forest/5 transition-colors"
            :disabled="saving"
            @click="resetDraft"
          >
            Annulla
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { updateGuest } from '../services/api'
import { ALLERGEN_OPTIONS, RSVP_EVENT_OPTIONS, getGuestAttendanceState } from '../constants/rsvp'

const props = defineProps({
  guest: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['updated', 'completed', 'close', 'saved'])

const saving = ref(false)
const saveError = ref('')
const draft = reactive({
  attend_ceremony: null,
  attend_lunch: null,
  allergens: []
})
const baseline = ref({
  attend_ceremony: null,
  attend_lunch: null,
  allergens: []
})
const forceShowEventDetails = ref(false)
const submissionFeedback = ref('')
const allergensOpen = ref(false)
const allergensPanel = ref(null)
const allergensToggleButton = ref(null)
const allergensJustOpened = ref(false)
const allergensReturnScrollY = ref(null)
let completionTimerId = null
let allergensFlashTimerId = null

const draftOverallChoice = computed(() => {
  if (draft.attend_ceremony === false && draft.attend_lunch === false) return 'decline'
  if (draft.attend_ceremony === true || draft.attend_lunch === true) return 'attend'
  return null
})

const showEventDetails = computed(() => forceShowEventDetails.value || draftOverallChoice.value === 'attend')

const normalizedDraft = computed(() => ({
  attend_ceremony: draft.attend_ceremony,
  attend_lunch: draft.attend_lunch,
  allergens: [...draft.allergens].sort()
}))

const normalizedBaseline = computed(() => ({
  attend_ceremony: baseline.value.attend_ceremony,
  attend_lunch: baseline.value.attend_lunch,
  allergens: [...baseline.value.allergens].sort()
}))

const isDirty = computed(() => JSON.stringify(normalizedDraft.value) !== JSON.stringify(normalizedBaseline.value))
const selectedAllergenCount = computed(() => draft.allergens.length)
const selectedAllergenLabels = computed(() => {
  const labelsByValue = new Map(ALLERGEN_OPTIONS.map(option => [option.value, option.label]))
  return draft.allergens.map(value => labelsByValue.get(value) || value)
})
const allergensSummaryText = computed(() => {
  if (selectedAllergenCount.value === 0) return 'Nessuno selezionato'
  if (selectedAllergenCount.value <= 2) return selectedAllergenLabels.value.join(', ')
  return `${selectedAllergenCount.value} selezionati`
})

function snapshotFromGuest(guest) {
  const state = getGuestAttendanceState(guest)
  const allergens = Array.isArray(guest?.allergens) ? [...guest.allergens] : []
  return {
    attend_ceremony: state.attend_ceremony,
    attend_lunch: state.attend_lunch,
    allergens
  }
}

function applySnapshot(snapshot) {
  draft.attend_ceremony = snapshot.attend_ceremony
  draft.attend_lunch = snapshot.attend_lunch
  draft.allergens = [...snapshot.allergens]
  forceShowEventDetails.value = snapshot.attend_ceremony === true || snapshot.attend_lunch === true
  allergensOpen.value = snapshot.allergens.length > 0
  saveError.value = ''
}

function resetDraft() {
  applySnapshot(baseline.value)
}

function clearCompletionTimer() {
  if (completionTimerId) {
    clearTimeout(completionTimerId)
    completionTimerId = null
  }
}

function clearAllergensFlashTimer() {
  if (allergensFlashTimerId) {
    clearTimeout(allergensFlashTimerId)
    allergensFlashTimerId = null
  }
}

function restoreScrollAfterAllergensClose() {
  if (allergensReturnScrollY.value == null) return
  if (typeof window !== 'undefined' && typeof window.scrollTo === 'function') {
    window.scrollTo({ top: allergensReturnScrollY.value, behavior: 'smooth' })
  }
  allergensReturnScrollY.value = null
}

function requestClose() {
  if (saving.value) return
  if (!submissionFeedback.value && isDirty.value) {
    const ok = window.confirm('Hai modifiche non salvate. Vuoi chiudere senza salvare?')
    if (!ok) return
  }
  clearCompletionTimer()
  submissionFeedback.value = ''
  emit('close')
}

watch(
  () => props.guest,
  (guest) => {
    const snap = snapshotFromGuest(guest)
    baseline.value = snap
    applySnapshot(snap)
  },
  { immediate: true, deep: true }
)

function confirmIfNeeded() {
  if (sessionStorage.getItem('rsvp_updated') === 'pending') {
    if (!window.confirm(`Stai modificando la partecipazione di ${props.guest.name}.\nClicca OK per procedere comunque.`)) return false
    sessionStorage.setItem('rsvp_updated', 'confirmed')
  }
  return true
}

function selectAttending() {
  if (saving.value) return
  forceShowEventDetails.value = true
  draft.attend_ceremony = true
  draft.attend_lunch = true
}

function selectDecline() {
  if (saving.value) return
  forceShowEventDetails.value = false
  draft.attend_ceremony = false
  draft.attend_lunch = false
}

function setEventAttendance(field, value) {
  if (saving.value) return
  draft[field] = value
  if (value === true) {
    forceShowEventDetails.value = true
  } else if (draft.attend_ceremony === false && draft.attend_lunch === false) {
    forceShowEventDetails.value = false
  }
}

function toggleAllergensAccordion() {
  if (saving.value) return
  if (allergensOpen.value) {
    allergensOpen.value = false
    restoreScrollAfterAllergensClose()
    return
  }

  if (typeof window !== 'undefined') {
    allergensReturnScrollY.value = window.scrollY
  }
  allergensOpen.value = true
  if (allergensOpen.value) {
    nextTick(() => {
      allergensJustOpened.value = true
      clearAllergensFlashTimer()
      allergensFlashTimerId = setTimeout(() => {
        allergensJustOpened.value = false
      }, 700)

      const headerEl = allergensToggleButton.value
      if (headerEl && typeof headerEl.scrollIntoView === 'function') {
        headerEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
      } else if (allergensPanel.value && typeof allergensPanel.value.scrollIntoView === 'function') {
        allergensPanel.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    })
  }
}

function closeAllergensAccordion() {
  if (saving.value || !allergensOpen.value) return
  allergensOpen.value = false
  restoreScrollAfterAllergensClose()
}

function toggleAllergen(allergen) {
  if (saving.value) return
  if (draft.allergens.includes(allergen)) {
    draft.allergens = draft.allergens.filter(item => item !== allergen)
  } else {
    draft.allergens = [...draft.allergens, allergen]
  }
}

async function saveDraft() {
  if (saving.value || !isDirty.value) return
  if (!confirmIfNeeded()) return

  saving.value = true
  saveError.value = ''
  try {
    const updated = await updateGuest(props.guest.id, {
      attend_ceremony: draft.attend_ceremony,
      attend_lunch: draft.attend_lunch,
      allergens: [...draft.allergens]
    })
    if (!sessionStorage.getItem('rsvp_updated')) sessionStorage.setItem('rsvp_updated', 'pending')
    baseline.value = snapshotFromGuest(updated)
    applySnapshot(baseline.value)
    emit('updated', updated)
    const hasAtLeastOnePresence = updated.attend_ceremony === true || updated.attend_lunch === true
    const firstName = (updated.name || '').trim().split(/\s+/)[0] || updated.name || ''
    submissionFeedback.value = hasAtLeastOnePresence
      ? `Grazie ${firstName} per la tua presenza, ci vediamo presto per festeggiare insieme`
      : 'Ci dispiace che non potrai esserci, ci saranno altre occasioni per celebrare insieme'
    emit('saved', updated)
    clearCompletionTimer()
    completionTimerId = setTimeout(() => {
      submissionFeedback.value = ''
      emit('completed', updated)
    }, 5000)
  } catch (error) {
    saveError.value = 'Errore nel salvataggio. Riprova.'
    console.error('Failed to save single guest RSVP:', error)
  } finally {
    saving.value = false
  }
}

onBeforeUnmount(() => {
  clearCompletionTimer()
  clearAllergensFlashTimer()
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

.allergens-panel-flash {
  animation: allergens-panel-flash 0.65s ease-out;
}

@keyframes allergens-panel-flash {
  0% {
    box-shadow: 0 0 0 0 rgba(61, 79, 61, 0.28);
    background-color: rgba(245, 242, 235, 0.95);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(61, 79, 61, 0.12);
    background-color: rgba(238, 245, 230, 0.98);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(61, 79, 61, 0);
    background-color: rgba(245, 242, 235, 0.88);
  }
}
</style>
