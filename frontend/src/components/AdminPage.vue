<template>
  <div class="min-h-screen bg-sage pb-20">
    <AdminLogin v-if="!authenticated" @authenticated="authenticated = true" />
    <AdminDashboard v-else />
    
    <!-- Back to site link -->
    <div class="fixed bottom-6 left-1/2 -translate-x-1/2 z-40">
      <a 
        href="/" 
        class="bg-white/90 backdrop-blur-sm border border-forest/20 text-forest px-6 py-2 rounded-full shadow-lg hover:bg-white transition-all font-serif flex items-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Torna al Sito
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AdminLogin from './AdminLogin.vue'
import AdminDashboard from './AdminDashboard.vue'

const authenticated = ref(!!sessionStorage.getItem('admin_password'))
</script>
