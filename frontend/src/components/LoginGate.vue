<template>
  <div class="min-h-screen bg-sage flex items-center justify-center p-6">
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-10 w-full max-w-sm text-center">
      <h1 class="font-serif text-3xl text-stone-700 mb-2">Edoardo & Caterina</h1>
      <p class="text-stone-500 text-sm mb-8">Inserisci la password per accedere</p>

      <form @submit.prevent="submit">
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          class="w-full border border-stone-300 rounded-lg px-4 py-3 text-stone-700 focus:outline-none focus:ring-2 focus:ring-stone-400 mb-4"
          autofocus
        />
        <p v-if="error" class="text-red-400 text-sm mb-4">Password errata</p>
        <button
          type="submit"
          class="w-full bg-stone-600 hover:bg-stone-700 text-white rounded-lg px-4 py-3 transition-colors"
        >
          Entra
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const PASSWORD = 'OscarDorotea!'

const emit = defineEmits(['unlocked'])

const password = ref('')
const error = ref(false)

function submit() {
  if (password.value === PASSWORD) {
    emit('unlocked')
  } else {
    error.value = true
    password.value = ''
  }
}
</script>
