<template>
  <header
    :class="[
      'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
      scrolled ? 'bg-white shadow-md' : 'bg-transparent'
    ]"
  >
    <div class="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
      <!-- Logo -->
      <router-link to="/" class="flex items-center gap-2 no-underline">
        <div class="w-9 h-9 rounded-lg bg-primary-600 flex items-center justify-center">
          <i class="pi pi-chart-bar text-white text-base"></i>
        </div>
        <div>
          <span :class="['font-bold text-lg leading-none', scrolled ? 'text-primary-700' : 'text-white']">DTSEN</span>
          <span :class="['block text-xs leading-none', scrolled ? 'text-gray-400' : 'text-primary-200']">Zakat & Wakaf</span>
        </div>
      </router-link>

      <!-- Desktop nav -->
      <nav class="hidden md:flex items-center gap-6">
        <a
          v-for="item in navItems"
          :key="item.href"
          :href="item.href"
          :class="[
            'text-sm font-medium transition-colors hover:text-primary-400',
            scrolled ? 'text-gray-700' : 'text-primary-100'
          ]"
        >{{ item.label }}</a>
      </nav>

      <!-- CTA -->
      <div class="flex items-center gap-2">
        <Button
          label="Masuk"
          icon="pi pi-sign-in"
          size="small"
          :outlined="!scrolled"
          :class="!scrolled ? 'text-white border-white hover:bg-white/20' : ''"
          @click="$router.push('/login')"
        />
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Button from 'primevue/button'

const scrolled = ref(false)
const navItems = [
  { label: 'Beranda',   href: '#hero' },
  { label: 'Statistik', href: '#stats' },
  { label: 'Peta',      href: '#map' },
  { label: 'Program',   href: '#program' },
  { label: 'Tentang',   href: '#tentang' },
]

function onScroll() { scrolled.value = window.scrollY > 40 }
onMounted(() => window.addEventListener('scroll', onScroll))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>
