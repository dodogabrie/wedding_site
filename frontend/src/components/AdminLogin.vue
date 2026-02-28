<template>
  <div class="min-h-screen bg-sage flex items-center justify-center p-6">
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-10 w-full max-w-sm text-center">
      <h1 class="font-script text-4xl text-forest mb-2">Admin Dashboard</h1>
      <p class="font-serif text-stone-500 text-sm mb-8 italic">Area riservata per la gestione degli inviti</p>

      <form @submit.prevent="submit">
        <input
          v-model="password"
          type="password"
          placeholder="Password Admin"
          class="w-full border border-stone-300 rounded-lg px-4 py-3 text-stone-700 focus:outline-none focus:ring-2 focus:ring-forest mb-4 font-serif"
          autofocus
        />
        <p v-if="error" class="text-red-400 text-sm mb-4 font-serif">Password errata</p>
        <button
          type="submit"
          class="w-full bg-forest hover:bg-forest-dark text-white rounded-lg px-4 py-3 transition-colors font-serif text-lg"
          :disabled="loading"
        >
          {{ loading ? 'Verifica...' : 'Accedi' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { adminApi } from '../services/api'

const emit = defineEmits(['authenticated'])

const password = ref('')
const error = ref(false)
const loading = ref(false)

async function submit() {
  if (!password.value) return
  
  loading.value = true
  error.value = false
  
  try {
    // Attempt to fetch data to verify password
    sessionStorage.setItem('admin_password', password.value)
    await adminApi.getData()
    emit('authenticated')
  } catch (err) {
    error.value = true
    password.value = ''
    sessionStorage.removeItem('admin_password')
  } finally {
    loading.value = false
  }
}
</script>
