<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-800 to-primary-600">
    <!-- Navbar -->
    <nav class="flex items-center justify-between px-8 py-4">
      <div class="flex items-center gap-2 text-white">
        <i class="pi pi-chart-bar text-2xl text-secondary"></i>
        <span class="font-bold text-xl">DTSEN</span>
      </div>
      <Button label="Login" icon="pi pi-sign-in" outlined class="text-white border-white hover:bg-white/10" @click="$router.push('/login')" />
    </nav>

    <!-- Hero -->
    <div class="flex flex-col items-center justify-center text-center px-4 py-24">
      <Tag value="Sistem Informasi Zakat Nasional" severity="warning" class="mb-6 text-sm" />
      <h1 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">
        Data Tunggal Sosial Ekonomi Nasional
      </h1>
      <p class="text-primary-100 text-lg max-w-xl mb-8">
        Platform terpadu pemantauan penyaluran zakat dan wakaf berbasis data Bappenas & BAZNAS.
      </p>
      <div class="flex gap-3">
        <Button label="Lihat Dashboard" icon="pi pi-arrow-right" icon-pos="right" @click="$router.push('/dashboard')" />
        <Button label="Tentang Sistem" icon="pi pi-info-circle" outlined class="text-white border-white hover:bg-white/10" />
      </div>
    </div>

    <!-- Stats strip -->
    <div class="bg-white/10 backdrop-blur px-8 py-6">
      <div class="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center text-white">
        <div v-for="stat in stats" :key="stat.label">
          <p class="text-3xl font-bold text-secondary">{{ stat.value }}</p>
          <p class="text-sm text-primary-200 mt-1">{{ stat.label }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Button from 'primevue/button'
import Tag    from 'primevue/tag'

const stats = [
  { value: '34',    label: 'Provinsi' },
  { value: '500+',  label: 'LAZ Aktif' },
  { value: '3.2 Jt', label: 'Mustahik' },
  { value: 'Rp 8 T', label: 'Total Penyaluran' }
]
</script>
