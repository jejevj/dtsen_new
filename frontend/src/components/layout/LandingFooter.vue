<template>
  <footer class="bg-primary-950 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-14 pb-8">

      <!-- Top grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-10 pb-10 border-b border-primary-800">

        <!-- Brand -->
        <div class="lg:col-span-2">
          <div class="flex items-center gap-2.5 mb-4">
            <div class="w-9 h-9 rounded-xl bg-primary-600 flex items-center justify-center">
              <i class="pi pi-chart-bar text-white"></i>
            </div>
            <div>
              <div class="font-bold text-lg leading-none">DTSEN</div>
              <div class="text-xs text-primary-400 leading-none">Zakat &amp; Wakaf Nasional</div>
            </div>
          </div>
          <p class="text-primary-300 text-sm leading-relaxed max-w-xs mb-5">
            Platform pemantauan penyaluran zakat berbasis Data Tunggal Sosial Ekonomi Nasional (DTSEN)
            Bappenas. Transparan, terukur, tepat sasaran.
          </p>
          <!-- Badges -->
          <div class="flex flex-wrap gap-2">
            <span class="px-2.5 py-1 rounded-full bg-primary-800 text-primary-300 text-xs font-medium">Kementerian Agama RI</span>
            <span class="px-2.5 py-1 rounded-full bg-primary-800 text-primary-300 text-xs font-medium">BAZNAS</span>
            <span class="px-2.5 py-1 rounded-full bg-primary-800 text-primary-300 text-xs font-medium">Bappenas</span>
          </div>
        </div>

        <!-- Links -->
        <div>
          <h4 class="text-xs font-semibold uppercase tracking-widest text-primary-400 mb-4">Navigasi</h4>
          <ul class="space-y-2.5">
            <li v-for="item in footerLinks" :key="item.label">
              <a
                :href="item.href"
                class="flex items-center gap-2 text-sm text-primary-300 hover:text-white transition-colors group"
              >
                <i :class="item.icon + ' text-xs text-primary-500 group-hover:text-primary-300 transition-colors'"></i>
                {{ item.label }}
              </a>
            </li>
          </ul>
        </div>

        <!-- Contact -->
        <div>
          <h4 class="text-xs font-semibold uppercase tracking-widest text-primary-400 mb-4">Kontak</h4>
          <ul class="space-y-2.5">
            <li class="flex items-start gap-2 text-sm text-primary-300">
              <i class="pi pi-envelope text-xs mt-0.5 text-primary-500 flex-shrink-0"></i>
              <span>info@dtsen.kemenag.go.id</span>
            </li>
            <li class="flex items-start gap-2 text-sm text-primary-300">
              <i class="pi pi-map-marker text-xs mt-0.5 text-primary-500 flex-shrink-0"></i>
              <span>Jl. Lapangan Banteng Barat No.3-4, Jakarta Pusat</span>
            </li>
          </ul>
          <div class="flex gap-2 mt-5">
            <a
              v-for="social in socials"
              :key="social.icon"
              href="#"
              :class="['w-8 h-8 rounded-lg flex items-center justify-center transition-colors bg-primary-800 hover:bg-primary-700', social.color]"
            >
              <i :class="social.icon + ' text-sm'"></i>
            </a>
          </div>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="flex flex-col sm:flex-row items-center justify-between gap-3 pt-6 text-xs text-primary-400">
        <span>&copy; {{ year }} DTSEN — Hak Cipta Dilindungi</span>
        <div class="flex items-center gap-4">
          <a href="#" class="hover:text-white transition-colors">Kebijakan Privasi</a>
          <a href="#" class="hover:text-white transition-colors">Syarat Penggunaan</a>
          <span class="flex items-center gap-1">
            Dibangun dengan
            <i class="pi pi-heart text-red-400"></i>
            menggunakan Vue.js &amp; Flask
          </span>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()

const footerLinks = [
  { label: 'Statistik Nasional', href: '#stats',   icon: 'pi pi-chart-bar' },
  { label: 'Peta Sebaran',       href: '#map',     icon: 'pi pi-map' },
  { label: 'Program Zakat',      href: '#program', icon: 'pi pi-list' },
  { label: 'Login Sistem',       href: '/login',   icon: 'pi pi-sign-in' },
  { label: 'API Docs',           href: '#',        icon: 'pi pi-code' },
]

const socials = [
  { icon: 'pi pi-twitter',  color: 'text-sky-400' },
  { icon: 'pi pi-github',   color: 'text-white' },
  { icon: 'pi pi-youtube',  color: 'text-red-400' },
]
</script>
