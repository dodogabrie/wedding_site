<template>
  <div class="max-w-6xl mx-auto py-8 px-4 md:px-6">
    <header class="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
      <div>
        <h1 class="font-script text-5xl text-forest leading-tight">Admin Dashboard</h1>
        <p class="font-serif text-forest/70 italic">Gestione inviti e RSVP</p>
      </div>
      <div class="flex gap-2">
        <button 
          @click="showCreateFamilyModal = true"
          class="bg-forest/10 hover:bg-forest/20 text-forest border border-forest/30 px-4 py-2 rounded-xl transition-all font-serif flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Nuova Famiglia
        </button>
        <button 
          @click="openCreateGuestModal()"
          class="bg-forest text-cream hover:opacity-90 px-4 py-2 rounded-xl transition-all font-serif flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Nuovo Ospite
        </button>
      </div>
    </header>

    <!-- Stats Summary -->
    <div v-if="stats" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-cream rounded-2xl border border-forest/15 p-4 text-center shadow-sm">
        <p class="font-serif text-3xl text-forest">{{ stats.total_guests }}</p>
        <p class="font-serif text-xs text-forest/70 uppercase tracking-wider">Totale Ospiti</p>
      </div>
      <div class="bg-green-50 rounded-2xl border border-green-200 p-4 text-center shadow-sm">
        <p class="font-serif text-3xl text-green-800">{{ stats.confirmed }}</p>
        <p class="font-serif text-xs text-green-700 uppercase tracking-wider">Confermati</p>
      </div>
      <div class="bg-red-50 rounded-2xl border border-red-200 p-4 text-center shadow-sm">
        <p class="font-serif text-3xl text-red-800">{{ stats.declined }}</p>
        <p class="font-serif text-xs text-red-700 uppercase tracking-wider">Declinati</p>
      </div>
      <div class="bg-stone-50 rounded-2xl border border-stone-200 p-4 text-center shadow-sm">
        <p class="font-serif text-3xl text-stone-800">{{ stats.pending }}</p>
        <p class="font-serif text-xs text-stone-700 uppercase tracking-wider">In attesa</p>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="bg-cream rounded-2xl border border-forest/15 p-4 mb-6 shadow-sm flex flex-col md:flex-row gap-4 items-center">
      <div class="relative flex-1 w-full">
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-forest/40">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-4.35-4.35m1.85-5.15a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z" />
          </svg>
        </span>
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Cerca ospite o famiglia..." 
          class="w-full bg-white border border-forest/20 rounded-xl py-2 pl-10 pr-4 font-serif focus:outline-none focus:ring-2 focus:ring-forest/30"
        />
      </div>
      <div class="flex gap-2 w-full md:w-auto">
        <select 
          v-model="statusFilter"
          class="bg-white border border-forest/20 rounded-xl px-3 py-2 font-serif focus:outline-none focus:ring-2 focus:ring-forest/30 text-sm"
        >
          <option value="all">Tutti gli stati</option>
          <option value="confirmed">Confermati</option>
          <option value="declined">Declinati</option>
          <option value="pending">In attesa</option>
        </select>
      </div>
    </div>

    <!-- Data Table -->
    <div class="bg-cream rounded-2xl border border-forest/15 shadow-sm overflow-hidden mb-12">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[50rem]">
          <thead class="bg-forest text-cream font-serif">
            <tr>
              <th class="text-left px-4 py-3 text-sm font-medium">Nome</th>
              <th class="text-left px-4 py-3 text-sm font-medium">Gruppo</th>
              <th class="text-center px-4 py-3 text-sm font-medium">RSVP</th>
              <th class="text-left px-4 py-3 text-sm font-medium">Note Admin</th>
              <th class="text-right px-4 py-3 text-sm font-medium">Azioni</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-forest/10 font-serif">
            <tr 
              v-for="row in filteredRows" 
              :key="row.id"
              class="hover:bg-forest/5 transition-colors group"
              :class="row.isFamilyHeader ? 'bg-forest/5 font-semibold' : 'bg-white/40'"
            >
              <template v-if="row.isFamilyHeader">
                <td colspan="4" class="px-4 py-2 text-forest text-base">
                  <span class="flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    {{ row.name }} ({{ row.memberCount }} membri)
                  </span>
                </td>
                <td class="px-4 py-2 text-right">
                  <div class="flex justify-end gap-2">
                    <button @click="editFamily(row.data)" class="text-forest/60 hover:text-forest p-1">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                      </svg>
                    </button>
                    <button @click="deleteFamily(row.data)" class="text-red-400 hover:text-red-600 p-1">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h14" />
                      </svg>
                    </button>
                  </div>
                </td>
              </template>
              <template v-else>
                <td class="px-4 py-3 text-forest text-sm">
                  {{ row.name }}
                </td>
                <td class="px-4 py-3 text-forest/60 text-xs">
                  {{ row.family_name || 'Singolo' }}
                </td>
                <td class="px-4 py-3 text-center">
                  <span 
                    class="inline-block px-2 py-1 rounded-full text-[0.65rem] uppercase tracking-wider font-bold"
                    :class="statusClass(row.attending)"
                  >
                    {{ statusText(row.attending) }}
                  </span>
                </td>
                <td class="px-4 py-3 text-forest/70 text-xs italic max-w-[12rem] truncate">
                  {{ row.admin_notes || '-' }}
                </td>
                <td class="px-4 py-3 text-right">
                  <div class="flex justify-end gap-2">
                    <button @click="editGuest(row)" class="bg-forest/10 hover:bg-forest/20 text-forest p-1.5 rounded-lg transition-colors">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                      </svg>
                    </button>
                    <button @click="confirmDeleteGuest(row)" class="bg-red-50 hover:bg-red-100 text-red-600 p-1.5 rounded-lg transition-colors">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h14" />
                      </svg>
                    </button>
                  </div>
                </td>
              </template>
            </tr>
            <tr v-if="filteredRows.length === 0">
              <td colspan="5" class="px-4 py-8 text-center text-forest/50 italic">
                Nessun risultato trovato
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Guest Modal -->
    <div v-if="activeEditGuest" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-forest/40 backdrop-blur-sm">
      <div class="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden border border-forest/10">
        <div class="bg-forest p-6 text-cream">
          <h2 class="font-serif text-2xl">Modifica Ospite</h2>
          <p class="text-sm opacity-80">{{ activeEditGuest.name }}</p>
        </div>
        <div class="p-6 space-y-4 font-serif">
          <div>
            <label class="block text-xs text-forest/60 uppercase tracking-widest mb-1">Nome Ospite</label>
            <input v-model="editForm.name" type="text" class="w-full border border-forest/20 rounded-xl px-4 py-2 focus:ring-2 focus:ring-forest/20 outline-none" />
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs text-forest/60 uppercase tracking-widest mb-1">Famiglia / Gruppo</label>
              <select v-model="editForm.family_id" class="w-full border border-forest/20 rounded-xl px-4 py-2 focus:ring-2 focus:ring-forest/20 outline-none bg-white">
                <option :value="null">Nessuna (Ospite Singolo)</option>
                <option v-for="fam in families" :key="fam.id" :value="fam.id">{{ fam.family_name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-forest/60 uppercase tracking-widest mb-1">RSVP Globale</label>
              <select v-model="editForm.attending" class="w-full border border-forest/20 rounded-xl px-4 py-2 focus:ring-2 focus:ring-forest/20 outline-none bg-white">
                <option :value="null">In attesa</option>
                <option :value="true">Confermato (Si)</option>
                <option :value="false">Rifiutato (No)</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 pt-2">
            <div class="flex items-center gap-2">
              <input type="checkbox" v-model="editForm.attend_ceremony" id="check-ceremony" class="accent-forest w-4 h-4" />
              <label for="check-ceremony" class="text-sm text-forest">Cerimonia</label>
            </div>
            <div class="flex items-center gap-2">
              <input type="checkbox" v-model="editForm.attend_lunch" id="check-lunch" class="accent-forest w-4 h-4" />
              <label for="check-lunch" class="text-sm text-forest">Pranzo</label>
            </div>
          </div>

          <div>
            <label class="block text-xs text-forest/60 uppercase tracking-widest mb-1">Note Dietetiche (Ospite)</label>
            <p class="text-xs text-forest/50 mb-1 italic">Visto dall'ospite</p>
            <textarea v-model="editForm.dietary_notes" rows="2" class="w-full border border-forest/20 rounded-xl px-4 py-2 focus:ring-2 focus:ring-forest/20 outline-none resize-none"></textarea>
          </div>

          <div>
            <label class="block text-xs text-forest/60 uppercase tracking-widest mb-1">Note Admin (Segrete)</label>
            <p class="text-xs text-forest/50 mb-1 italic">Solo per te</p>
            <textarea v-model="editForm.admin_notes" rows="2" class="w-full border border-forest/20 rounded-xl px-4 py-2 focus:ring-2 focus:ring-forest/20 outline-none resize-none"></textarea>
          </div>
        </div>
        <div class="p-6 bg-stone-50 border-t border-forest/5 flex gap-3">
          <button @click="activeEditGuest = null" class="flex-1 bg-white border border-forest/20 text-forest py-2.5 rounded-xl hover:bg-forest/5 transition-colors">
            Annulla
          </button>
          <button @click="saveGuestUpdate" class="flex-1 bg-forest text-cream py-2.5 rounded-xl hover:opacity-90 transition-all flex items-center justify-center gap-2">
            <span v-if="saving">Salvataggio...</span>
            <span v-else>Salva Modifiche</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Create Family Modal -->
    <div v-if="showCreateFamilyModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-forest/40 backdrop-blur-sm">
      <div class="bg-white rounded-3xl shadow-2xl w-full max-w-sm overflow-hidden">
        <div class="bg-forest p-6 text-cream">
          <h2 class="font-serif text-2xl">Nuova Famiglia</h2>
        </div>
        <div class="p-6 font-serif">
          <label class="block text-xs text-forest/60 uppercase tracking-widest mb-1">Nome della Famiglia</label>
          <input v-model="newFamilyName" type="text" placeholder="es. Famiglia Rossi" class="w-full border border-forest/20 rounded-xl px-4 py-2 focus:ring-2 focus:ring-forest/20 outline-none" autofocus />
        </div>
        <div class="p-6 bg-stone-50 border-t border-forest/5 flex gap-3">
          <button @click="showCreateFamilyModal = false" class="flex-1 bg-white border border-forest/20 text-forest py-2 rounded-xl">Annulla</button>
          <button @click="createFamily" class="flex-1 bg-forest text-cream py-2 rounded-xl" :disabled="!newFamilyName">Crea</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi, getStats } from '../services/api'

const families = ref([])
const individuals = ref([])
const stats = ref(null)
const loading = ref(true)
const saving = ref(false)

const searchQuery = ref('')
const statusFilter = ref('all')

const activeEditGuest = ref(null)
const editForm = ref({})

const showCreateFamilyModal = ref(false)
const newFamilyName = ref('')

async function refreshData() {
  try {
    const [data, rsvpStats] = await Promise.all([
      adminApi.getData(),
      getStats()
    ])
    families.value = data.families
    individuals.value = data.individuals
    stats.value = rsvpStats
  } catch (err) {
    console.error('Failed to load admin data:', err)
  } finally {
    loading.value = false
  }
}

onMounted(refreshData)

const filteredRows = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  const rows = []

  // Process Families
  families.value.forEach(fam => {
    const familyMembers = fam.guests.filter(g => {
      const matchesSearch = !query || g.name.toLowerCase().includes(query) || fam.family_name.toLowerCase().includes(query)
      const matchesStatus = statusFilter.value === 'all' || 
        (statusFilter.value === 'confirmed' && g.attending === true) ||
        (statusFilter.value === 'declined' && g.attending === false) ||
        (statusFilter.value === 'pending' && g.attending === null)
      return matchesSearch && matchesStatus
    })

    if (familyMembers.length > 0) {
      // Add family header row
      rows.push({
        id: `fam-header-${fam.id}`,
        isFamilyHeader: true,
        name: fam.family_name,
        memberCount: fam.guests.length,
        data: fam
      })
      // Add member rows
      familyMembers.forEach(m => {
        rows.push({
          ...m,
          family_name: fam.family_name
        })
      })
    }
  })

  // Process Standalone Individuals
  const standalone = individuals.value.filter(g => {
    const matchesSearch = !query || g.name.toLowerCase().includes(query)
    const matchesStatus = statusFilter.value === 'all' || 
      (statusFilter.value === 'confirmed' && g.attending === true) ||
      (statusFilter.value === 'declined' && g.attending === false) ||
      (statusFilter.value === 'pending' && g.attending === null)
    return matchesSearch && matchesStatus
  })

  if (standalone.length > 0) {
    rows.push({
      id: 'standalone-header',
      isFamilyHeader: true,
      name: 'Ospiti Singoli',
      memberCount: standalone.length,
      data: null
    })
    standalone.forEach(g => {
      rows.push({
        ...g,
        family_name: null
      })
    })
  }

  return rows
})

function statusText(attending) {
  if (attending === true) return 'Si'
  if (attending === false) return 'No'
  return '?'
}

function statusClass(attending) {
  if (attending === true) return 'bg-green-100 text-green-800'
  if (attending === false) return 'bg-red-100 text-red-800'
  return 'bg-stone-100 text-stone-600'
}

function editGuest(guest) {
  activeEditGuest.value = guest
  editForm.value = { ...guest }
}

async function saveGuestUpdate() {
  saving.value = true
  try {
    await adminApi.updateGuest(activeEditGuest.value.id, editForm.value)
    activeEditGuest.value = null
    await refreshData()
  } catch (err) {
    alert('Errore durante il salvataggio')
  } finally {
    saving.value = false
  }
}

async function createFamily() {
  try {
    await adminApi.createFamily({ family_name: newFamilyName.value })
    newFamilyName.value = ''
    showCreateFamilyModal.value = false
    await refreshData()
  } catch (err) {
    alert('Errore durante la creazione')
  }
}

async function editFamily(family) {
  const newName = prompt('Nuovo nome per la famiglia:', family.family_name)
  if (newName && newName !== family.family_name) {
    try {
      await adminApi.updateFamily(family.id, { family_name: newName })
      await refreshData()
    } catch (err) {
      alert('Errore durante la modifica')
    }
  }
}

async function deleteFamily(family) {
  if (confirm(`Sei sicuro di voler eliminare la famiglia "${family.family_name}"? I membri NON verranno eliminati, ma diventeranno ospiti singoli.`)) {
    try {
      await adminApi.deleteFamily(family.id)
      await refreshData()
    } catch (err) {
      alert("Errore durante l'eliminazione")
    }
  }
}

async function confirmDeleteGuest(guest) {
  if (confirm(`Sei sicuro di voler eliminare l'ospite "${guest.name}"?`)) {
    try {
      await adminApi.deleteGuest(guest.id)
      await refreshData()
    } catch (err) {
      alert("Errore durante l'eliminazione")
    }
  }
}

async function openCreateGuestModal() {
  const name = prompt('Nome del nuovo ospite:')
  if (name) {
    try {
      await adminApi.createGuest({ name })
      await refreshData()
    } catch (err) {
      alert('Errore durante la creazione')
    }
  }
}
</script>
