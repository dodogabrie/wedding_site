<template>
    <!-- Pag da rimuovere mettendo solo l'IBAN e Tenerife! -->
    <!-- IBAN: IT18A0306921531100000006622 -->
    <!-- Intestatario: Caterina Betti Becucci -->

    <section class="relative min-h-screen py-20 px-4 pb-32 sm:pb-40">
        <!-- Bottom corner ornaments (vertically mirrored from top) -->
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

        <div class="max-w-3xl mx-auto">
            <!-- Header -->
            <h2
                ref="header"
                class="font-script text-forest text-4xl md:text-5xl lg:text-6xl text-center mb-16 opacity-0"
            >
                Programma
            </h2>

            <!-- Timeline -->
            <div ref="timeline" class="relative">
                <!-- Vertical line -->
                <div
                    class="absolute left-4 md:left-8 top-0 bottom-0 w-0.5 bg-forest/30"
                ></div>

                <!-- Timeline items -->
                <div class="space-y-6 md:space-y-8">
                    <div
                        v-for="(item, index) in program"
                        :key="index"
                        class="timeline-item flex items-center gap-4 md:gap-6 opacity-0"
                    >
                        <!-- Left: Time + dot -->
                        <div
                            class="relative flex-shrink-0 w-24 sm:w-28 md:w-32"
                        >
                            <div
                                class="absolute left-4 md:left-8 top-1/2 -translate-y-1/2 -translate-x-1/2 w-3 h-3 bg-forest rounded-full z-10"
                            ></div>
                            <span
                                class="block text-forest font-serif text-2xl sm:text-2xl md:text-3xl font-medium pl-12 md:pl-16"
                            >
                                {{ item.time }}
                            </span>
                        </div>

                        <!-- Center: Event description -->
                        <div class="flex-1">
                            <h3
                                class="text-forest font-serif text-2xl sm:text-2xl md:text-3xl font-medium"
                            >
                                {{ item.title }}
                            </h3>
                            <p
                                v-if="item.description"
                                class="text-forest/80 font-serif mt-1 text-lg sm:text-xl md:text-xl"
                            >
                                {{ item.description }}
                            </p>
                        </div>

                        <!-- Right: Venue illustration -->
                        <div class="flex-shrink-0 w-20 sm:w-28 md:w-40 lg:w-48">
                            <img
                                v-if="item.image"
                                :src="item.image"
                                :alt="item.venue"
                                class="w-full"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import cornerSvg from "../assets/corner.svg";
import palazzoComunale from "../assets/palazzo_comunale.webp";
import serraMontu from "../assets/serra_montu.webp";

gsap.registerPlugin(ScrollTrigger);

const header = ref(null);
const timeline = ref(null);

const program = [
    {
        time: "11:30",
        title: "Cerimonia civile",
        description: "Celebrazione del matrimonio",
        venue: "Palazzo degli Anziani",
        image: palazzoComunale,
    },
    {
        time: "13:00",
        title: "Aperitivo",
        description: "Brindisi e stuzzichini di benvenuto",
        venue: "Serra Montu",
        image: serraMontu,
    },
    {
        time: "14:30",
        title: "Pranzo",
        description: "Pranzo nuziale",
        venue: "Serra Montu",
        image: null,
    },
    {
        time: "17:00",
        title: "Taglio della torta",
        description: "",
        venue: "Serra Montu",
        image: null,
    },
    {
        time: "18:00",
        title: "Festa",
        description: "Musica e divertimento",
        venue: "Serra Montu",
        image: null,
    },
];

onMounted(() => {
    // Animate header
    gsap.to(header.value, {
        opacity: 1,
        y: 0,
        duration: 0.8,
        scrollTrigger: {
            trigger: header.value,
            start: "top 80%",
            toggleActions: "play none none reverse",
        },
    });

    // Animate timeline items with stagger
    const items = document.querySelectorAll(".timeline-item");
    gsap.to(items, {
        opacity: 1,
        y: 0,
        duration: 0.6,
        stagger: 0.2,
        scrollTrigger: {
            trigger: timeline.value,
            start: "top 70%",
            toggleActions: "play none none reverse",
        },
    });
});
</script>
