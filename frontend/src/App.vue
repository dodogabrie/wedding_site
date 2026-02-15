<template>
  <div class="min-h-screen bg-sage p-2 md:p-4 lg:p-6">
    <IntroHero />
    <RSVPSection />
    <ContributionPage />
  </div>
</template>

<script setup>
import IntroHero from './components/IntroHero.vue'
import RSVPSection from './components/RSVPSection.vue'
import ContributionPage from './components/ContributionPage.vue'
</script>
