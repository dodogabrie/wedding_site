<template>
  <section class="min-h-screen py-10 px-4 md:px-6">
    <div class="max-w-5xl mx-auto">
      <header class="text-center mb-8 md:mb-10">
        <h1 class="font-script text-5xl md:text-6xl text-forest leading-[1.2]">Riepilogo</h1>
      </header>

      <div v-if="loading" class="text-center text-forest">
        <p class="font-serif text-lg">Caricamento riepilogo...</p>
      </div>

      <div v-else-if="error" class="text-center text-red-800">
        <p class="font-serif text-lg">{{ error }}</p>
      </div>

      <div v-else class="space-y-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-cream rounded-2xl border border-forest/15 p-5 text-center shadow-sm">
            <p class="font-serif text-4xl text-forest">{{ yesCount }}</p>
            <p class="font-serif text-forest/80">{{ yesCount }} persone hanno detto si</p>
          </div>
          <div class="bg-cream rounded-2xl border border-forest/15 p-5 text-center shadow-sm">
            <p class="font-serif text-4xl text-forest">{{ noCount }}</p>
            <p class="font-serif text-forest/80">{{ noCount }} persone hanno detto no</p>
          </div>
          <div class="bg-cream rounded-2xl border border-forest/15 p-5 text-center shadow-sm">
            <p class="font-serif text-4xl text-forest">{{ pendingCount }}</p>
            <p class="font-serif text-forest/80">{{ pendingCount }} persone non hanno risposto</p>
          </div>
        </div>

        <div class="bg-cream rounded-2xl border border-forest/15 shadow-sm overflow-hidden">
          <div class="px-4 py-3 border-b border-forest/10 bg-cream-dark/70">
            <p class="font-serif text-forest text-lg">Dettaglio ospiti</p>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full min-w-[36rem]">
              <thead class="bg-forest/5">
                <tr>
                  <th class="text-left px-4 py-3 font-serif text-forest">Nome</th>
                  <th class="text-left px-4 py-3 font-serif text-forest">Gruppo</th>
                  <th class="text-left px-4 py-3 font-serif text-forest">Tipo</th>
                  <th class="text-left px-4 py-3 font-serif text-forest">Risposta</th>
                </tr>
              </thead>
              <tbody>
                <template v-if="individualRows.length > 0">
                  <tr class="border-t border-forest/10 bg-forest/5">
                    <td colspan="4" class="px-4 py-2 font-serif text-forest">Ospiti singoli</td>
                  </tr>
                  <tr
                    v-for="guest in individualRows"
                    :key="guest.id"
                    class="border-t border-forest/10"
                  >
                    <td class="px-4 py-3 font-serif text-forest">{{ guest.name }}</td>
                    <td class="px-4 py-3 font-serif text-forest/85">{{ guest.group }}</td>
                    <td class="px-4 py-3 font-serif text-forest/85">{{ guest.type }}</td>
                    <td class="px-4 py-3">
                      <span
                        class="inline-flex items-center rounded-full px-3 py-1 font-serif text-sm"
                        :class="statusClass(guest.attending)"
                      >
                        {{ statusText(guest.attending) }}
                      </span>
                    </td>
                  </tr>
                </template>

                <template v-for="family in familyGroups" :key="family.id">
                  <tr class="border-t border-forest/10 bg-forest/5">
                    <td colspan="4" class="px-4 py-2 font-serif text-forest">{{ family.family_name }}</td>
                  </tr>
                  <tr
                    v-for="guest in family.guests"
                    :key="guest.id"
                    class="border-t border-forest/10"
                  >
                    <td class="px-4 py-3 font-serif text-forest">{{ guest.name }}</td>
                    <td class="px-4 py-3 font-serif text-forest/85">{{ guest.group }}</td>
                    <td class="px-4 py-3 font-serif text-forest/85">{{ guest.type }}</td>
                    <td class="px-4 py-3">
                      <span
                        class="inline-flex items-center rounded-full px-3 py-1 font-serif text-sm"
                        :class="statusClass(guest.attending)"
                      >
                        {{ statusText(guest.attending) }}
                      </span>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { getFamilies, getGuests } from '../services/api'

const loading = ref(true)
const error = ref(null)
const families = ref([])
const individualGuests = ref([])

const individualRows = computed(() =>
  individualGuests.value
    .map((guest) => ({
      id: `single-${guest.id}`,
      name: guest.name,
      group: 'Ospite singolo',
      type: 'Singolo',
      attending: guest.attending
    }))
    .sort((a, b) => a.name.localeCompare(b.name, 'it'))
)

const familyGroups = computed(() =>
  families.value
    .map((family) => ({
      id: family.id,
      family_name: family.family_name,
      guests: family.guests
        .map((guest) => ({
          id: `family-${guest.id}`,
          name: guest.name,
          group: family.family_name,
          type: 'Famiglia',
          attending: guest.attending
        }))
        .sort((a, b) => a.name.localeCompare(b.name, 'it'))
    }))
    .sort((a, b) => a.family_name.localeCompare(b.family_name, 'it'))
)

const allGuests = computed(() => [
  ...individualRows.value,
  ...familyGroups.value.flatMap((family) => family.guests)
])

const yesCount = computed(() => allGuests.value.filter((guest) => guest.attending === true).length)
const noCount = computed(() => allGuests.value.filter((guest) => guest.attending === false).length)
const pendingCount = computed(() => allGuests.value.filter((guest) => guest.attending === null).length)

function statusText(attending) {
  if (attending === true) return 'Si'
  if (attending === false) return 'No'
  return 'In attesa'
}

function statusClass(attending) {
  if (attending === true) return 'bg-green-100 text-green-800'
  if (attending === false) return 'bg-red-100 text-red-800'
  return 'bg-stone-100 text-stone-700'
}

onMounted(async () => {
  try {
    const [familiesData, guestsData] = await Promise.all([getFamilies(), getGuests()])
    families.value = familiesData
    individualGuests.value = guestsData
  } catch (err) {
    console.error(err)
    error.value = 'Errore nel caricamento del riepilogo RSVP.'
  } finally {
    loading.value = false
  }
})
</script>
