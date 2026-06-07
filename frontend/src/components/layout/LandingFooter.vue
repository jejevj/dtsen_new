<template>
  <footer class="bg-primary-900 text-white">
    <div class="max-w-7xl mx-auto px-6 py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- Brand -->
        <div class="md:col-span-2">
          <div class="flex items-center gap-2 mb-3">
            <div class="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
              <i class="pi pi-chart-bar text-white text-sm"></i>
            </div>
            <span class="font-bold text-lg">DTSEN</span>
          </div>
          <p class="text-primary-300 text-sm leading-relaxed max-w-xs">
            Sistem Informasi Zakat dan Wakaf Nasional berbasis Data Tunggal Sosial Ekonomi Nasional (DTSEN) Bappenas.
          </p>
          <div class="flex gap-3 mt-4">
            <a href="#" class="w-8 h-8 rounded-full bg-primary-700 flex items-center justify-center hover:bg-primary-600 transition-colors">
              <i class="pi pi-twitter text-xs"></i>
            </a>
            <a href="#" class="w-8 h-8 rounded-full bg-primary-700 flex items-center justify-center hover:bg-primary-600 transition-colors">
              <i class="pi pi-github text-xs"></i>
            </a>
          </div>
        </div>

        <!-- Links -->
        <div>
          <h4 class="font-semibold text-sm mb-3 text-primary-200 uppercase tracking-wider">Navigasi</h4>
          <ul class="space-y-2">
            <li v-for="item in links" :key="item.label">
              <a :href="item.href" class="text-sm text-primary-300 hover:text-white transition-colors">{{ item.label }}</a>
            </li>
          </ul>
        </div>

        <!-- Legal -->
        <div>
          <h4 class="font-semibold text-sm mb-3 text-primary-200 uppercase tracking-wider">Tentang</h4>
          <ul class="space-y-2">
            <li><a href="#" class="text-sm text-primary-300 hover:text-white transition-colors">Kebijakan Privasi</a></li>
            <li><a href="#" class="text-sm text-primary-300 hover:text-white transition-colors">Syarat Penggunaan</a></li>
            <li><a href="#" class="text-sm text-primary-300 hover:text-white transition-colors">Kontak</a></li>
          </ul>
        </div>
      </div>

      <Divider class="border-primary-700 my-8" />
      <div class="flex flex-col md:flex-row items-center justify-between gap-2 text-xs text-primary-400">
        <span>&copy; {{ year }} DTSEN — Kementerian Agama RI & BAZNAS</span>
        <span>Dibangun dengan Vue.js 3 + Flask</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
import Divider from 'primevue/divider'
const year  = new Date().getFullYear()
const links = [
  { label: 'Statistik Nasional', href: '#stats' },
  { label: 'Peta Sebaran',       href: '#map' },
  { label: 'Program Zakat',      href: '#program' },
  { label: 'Login Sistem',       href: '/login' },
]
</script>
