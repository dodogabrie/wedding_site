<template>
  <LoginGate v-if="!unlocked" @unlocked="unlocked = true" />
  <div v-else class="min-h-screen bg-sage p-2 md:p-4 lg:p-6">
    <IntroHero />
    <RSVPSection />
    <ContributionPage />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LoginGate from './components/LoginGate.vue'
import IntroHero from './components/IntroHero.vue'
import RSVPSection from './components/RSVPSection.vue'
import ContributionPage from './components/ContributionPage.vue'

const PASSWORD = 'OscarDorotea!'

function checkAccess() {
  // Magic link: /?key=OscarDorotea!
  const params = new URLSearchParams(window.location.search)
  if (params.get('key') === PASSWORD) {
    window.history.replaceState({}, '', window.location.pathname)
    return true
  }

  return false
}

const unlocked = ref(checkAccess())
</script>
