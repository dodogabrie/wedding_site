<template>
  <section class="relative -mt-40 md:-mt-52 px-4 pt-2 pb-12 sm:pb-32">
    <img
      :src="cornerSvg"
      alt=""
      class="absolute bottom-0 left-0 w-20 sm:w-32 md:w-48 lg:w-56 -rotate-90 -scale-y-100"
    />
    <img
      :src="cornerSvg"
      alt=""
      class="absolute bottom-0 right-0 w-20 sm:w-32 md:w-48 lg:w-56 rotate-90 -scale-x-100 -scale-y-100"
    />

    <div class="relative z-10 max-w-3xl mx-auto text-center">
      <p class="font-serif text-forest text-2xl sm:text-3xl md:text-4xl italic leading-[1.25] md:leading-[1.3]">
        <span class="block">La vostra presenza è per</span>
        <span class="block">noi il regalo più bello!</span>
      </p>

      <p class="font-serif text-forest/90 text-xl sm:text-2xl md:text-[2.05rem] italic mt-6 leading-[1.25] md:leading-[1.3]">
        <span class="block">Se tuttavia avete piacere, potete contribuire a</span>
        <span class="block">realizzare la nostra luna di miele dei sogni a</span>
      </p>

      <h2
        class="font-script text-forest leading-[0.85] mt-16 md:mt-24"
        style="font-size: clamp(4rem, 8.2vw, 6.2rem);"
      >
        Tenerife
      </h2>

      <div class="mt-8 flex flex-col items-center gap-6 md:mt-10 md:grid md:grid-cols-2 md:items-end md:gap-8 text-center md:text-left">
        <img
          :src="tenerife"
          alt="Isola di Tenerife"
          class="w-56 sm:w-64 md:w-80 lg:w-[27rem] opacity-70 md:justify-self-start md:-translate-x-10"
        />

        <div class="w-full px-4 sm:px-0 md:justify-self-end md:pb-3 md:translate-x-8 md:-translate-y-6">
          <p class="font-serif text-forest/90 text-xl sm:text-2xl md:text-3xl italic">il nostro iban è:</p>
          <div class="flex flex-col sm:flex-row items-center justify-center md:justify-start gap-2 sm:gap-3 mt-2">
            <p class="font-serif text-forest text-base sm:text-lg md:text-xl lg:text-[2rem] tracking-tight sm:tracking-normal lg:tracking-wide break-all sm:break-normal">
              IT18A0306921531100000006622
            </p>
            <button
              @click="copyIban"
              class="relative group px-3 py-2 sm:px-4 bg-forest/10 hover:bg-forest/20 rounded-lg border-2 border-forest/30 hover:border-forest/50 transition-all duration-300 active:scale-95 flex-shrink-0"
              :class="{ 'bg-forest/30 border-forest': copied }"
            >
              <svg
                v-if="!copied"
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5 text-forest"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5 text-forest animate-bounce"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="absolute -top-8 left-1/2 -translate-x-1/2 bg-forest text-sage px-3 py-1 rounded text-sm font-serif whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                {{ copied ? 'Copiato!' : 'Copia IBAN' }}
              </span>
            </button>
          </div>
          <p class="font-serif text-forest text-xl sm:text-2xl md:text-3xl mt-2">Caterina Betti Beccucci</p>
        </div>
      </div>

      <p class="font-serif text-forest text-2xl sm:text-3xl md:text-4xl italic mt-8">Grazie di cuore!</p>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import cornerSvg from '../assets/corner.svg'
import tenerife from '../assets/tenerife.png'

const copied = ref(false)
const iban = 'IT18A0306921531100000006622'

const copyIban = async () => {
  try {
    await navigator.clipboard.writeText(iban)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>
