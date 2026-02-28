<template>
  <LoginGate v-if="!unlocked" @unlocked="onUnlocked" />
  <div v-else class="min-h-screen bg-sage p-2 md:p-4 lg:p-6">
    <AdminPage v-if="isAdminRoute" />
    <SummaryPage v-else-if="isSummaryRoute" />
    <PhotoGallery v-else-if="isGalleryRoute" />
    <template v-else>
      <IntroHero />
      <RSVPSection />
      <ContributionPage />
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import LoginGate from './components/LoginGate.vue'
import IntroHero from './components/IntroHero.vue'
import RSVPSection from './components/RSVPSection.vue'
import ContributionPage from './components/ContributionPage.vue'
import SummaryPage from './components/SummaryPage.vue'
import PhotoGallery from './components/PhotoGallery.vue'
import AdminPage from './components/AdminPage.vue'

const PASSWORD = 'OscarDorotea!'
const ACCESS_STORAGE_KEY = 'wedding_site_access_granted'

function checkAccess() {
  if (window.localStorage.getItem(ACCESS_STORAGE_KEY) === '1') {
    return true
  }

  // Magic link: /?key=OscarDoroteaAdmin! or /summary?key=OscarDoroteaAdmin! or /admin?key=OscarDoroteaAdmin!
  const params = new URLSearchParams(window.location.search)
  if (params.get('key') === PASSWORD) {
    window.localStorage.setItem(ACCESS_STORAGE_KEY, '1')
    window.history.replaceState({}, '', window.location.pathname)
    return true
  }

  return false
}

const normalizedPath = window.location.pathname.replace(/\/+$/, '') || '/'
const isSummaryRoute = computed(() => normalizedPath === '/summary')
const isGalleryRoute = computed(() => normalizedPath === '/gallery')
const isAdminRoute = computed(() => normalizedPath === '/admin')
const unlocked = ref(checkAccess())

function onUnlocked() {
  window.localStorage.setItem(ACCESS_STORAGE_KEY, '1')
  unlocked.value = true
  window.scrollTo({ top: 0, left: 0, behavior: 'auto' })
}
</script>
