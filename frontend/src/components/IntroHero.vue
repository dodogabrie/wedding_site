<template>
  <section class="relative min-h-screen flex flex-col items-center justify-center px-4 overflow-x-hidden">
    <!-- Top left corner ornament -->
    <img
      ref="cornerTopLeft"
      :src="cornerSvg"
      alt=""
      class="absolute top-0 left-0 rotate-90 w-20 sm:w-32 md:w-48 lg:w-56 opacity-0"
    />
    <!-- Top right corner ornament (mirrored) -->
    <img
      ref="cornerTopRight"
      :src="cornerSvg"
      alt=""
      class="absolute top-0 right-0 -rotate-90 -scale-x-100 w-20 sm:w-32 md:w-48 lg:w-56 opacity-0"
    />

    <!-- Main content -->
    <div class="text-center z-10 max-w-2xl flex-1 flex flex-col justify-center">
      <p ref="subtitle" class="text-forest text-2xl md:text-4xl mt-5 mb-12 md:mb-12 opacity-0 font-serif italic">
        Siamo lieti di invitarvi<br>al nostro matrimonio
      </p>

      <h1 ref="names" class="font-script text-forest text-4xl md:text-7xl mt-4 mb-1 leading-[1.32] pt-6 pb-4 md:py-8">
        <span class="block text-center">
          <!-- mobile: whole word revealed by clip-path -->
          <span ref="edoardoMobile" class="md:hidden script-reveal-word">Edoardo</span>
          <!-- desktop: per-character animation -->
          <span
            v-for="(char, i) in 'Edoardo'"
            :key="'e'+i"
            class="hidden md:inline-block opacity-0"
            :ref="el => { if (el) edoardoChars[i] = el }"
          >{{ char }}</span>
        </span>
        <span class="block text-center text-3xl md:text-5xl py-2 md:py-4">
          <span ref="ampersandMobile" class="md:hidden script-reveal-word">&</span>
          <span ref="ampersand" class="hidden md:inline-block opacity-0">&</span>
        </span>
        <span class="block text-center mt-2 md:mt-4">
          <span ref="caterinaMobile" class="md:hidden script-reveal-word">Caterina</span>
          <span
            v-for="(char, i) in 'Caterina'"
            :key="'c'+i"
            class="hidden md:inline-block opacity-0"
            :ref="el => { if (el) caterinaChars[i] = el }"
          >{{ char }}</span>
        </span>
      </h1>

      <div ref="details" class="text-forest text-xl md:text-3xl mt-12 md:mt-10 opacity-0 font-serif">
        <p>Domenica 26 aprile 2026, ore 11:30</p>
        <p>Sala Maggiore del Palazzo degli Anziani,</p>
        <p>Pistoia</p>
      </div>
    </div>

    <!-- Decorative divider -->
    <div ref="divider" class="mt-8 sm:mt-12 opacity-0">
      <svg class="w-24 h-6 text-forest" viewBox="0 0 100 20" fill="currentColor">
        <path d="M0 10 Q 25 0, 50 10 T 100 10" stroke="currentColor" stroke-width="1" fill="none"/>
      </svg>
    </div>


  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { gsap } from 'gsap'

import cornerSvg from '../assets/corner.svg'

// Template refs
const cornerTopLeft = ref(null)
const cornerTopRight = ref(null)
const subtitle = ref(null)
const names = ref(null)
const details = ref(null)
const divider = ref(null)
const edoardoChars = ref([])
const caterinaChars = ref([])
const ampersand = ref(null)
const edoardoMobile = ref(null)
const caterinaMobile = ref(null)
const ampersandMobile = ref(null)

onMounted(() => {
  const tl = gsap.timeline({ defaults: { ease: 'power2.out' } })
  const isMobile = window.innerWidth < 768

  // Animate corners
  tl.to([cornerTopLeft.value, cornerTopRight.value], {
    opacity: 1,
    duration: 1,
    stagger: 0.2
  }, 0)

  // Animate text content
  tl.to(subtitle.value, {
    opacity: 1,
    y: 0,
    duration: 0.8
  }, 0.3)

  if (isMobile) {
    // Clip-path left-to-right reveal — keeps cursive ligatures intact
    // Use negative top/bottom insets so tall glyph flourishes are not clipped.
    const revealFrom = { clipPath: 'inset(-28% 100% -28% 0)' }
    const revealTo = { clipPath: 'inset(-28% 0% -28% 0)', duration: 1.0, ease: 'power2.inOut' }
    gsap.set([edoardoMobile.value, ampersandMobile.value, caterinaMobile.value], revealFrom)
    tl.to(edoardoMobile.value, revealTo, 0.6)
    tl.to(ampersandMobile.value, { ...revealTo, duration: 0.5 }, '>')
    tl.to(caterinaMobile.value, revealTo, '>')
    // Remove clip-path at rest to avoid any residual glyph clipping on some mobile renderers.
    tl.set([edoardoMobile.value, ampersandMobile.value, caterinaMobile.value], { clearProps: 'clipPath' })
  } else {
    // Per-character bounce animation for desktop
    tl.fromTo(edoardoChars.value,
      { opacity: 0, scale: 0.5, y: 20 },
      { opacity: 1, scale: 1, y: 0, duration: 0.3, stagger: 0.08, ease: 'back.out(1.7)' }, 0.6)

    tl.fromTo(ampersand.value,
      { opacity: 0, scale: 0.5, y: 20 },
      { opacity: 1, scale: 1, y: 0, duration: 0.4, ease: 'back.out(1.7)' }, '>')

    tl.fromTo(caterinaChars.value,
      { opacity: 0, scale: 0.5, y: 20 },
      { opacity: 1, scale: 1, y: 0, duration: 0.3, stagger: 0.08, ease: 'back.out(1.7)' }, '>')
  }

  tl.to(details.value, {
    opacity: 1,
    y: 0,
    duration: 0.8
  }, '+=0.3')

  tl.to(divider.value, {
    opacity: 1,
    duration: 0.6
  }, '>')
})
</script>

<style scoped>
.script-reveal-word {
  overflow: visible;
}

@media (max-width: 767px) {
  .script-reveal-word {
    display: inline-block;
  }
}
</style>
