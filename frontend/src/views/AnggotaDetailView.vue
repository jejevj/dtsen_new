<template>
  <AppLayout>
    <div class="space-y-5">

      <!-- Header -->
      <div class="flex items-center gap-3">
        <Button
          icon="pi pi-arrow-left" text rounded
          @click="$router.back()"
        />
        <div>
          <h2 class="text-xl font-bold text-slate-800">Detail Anggota</h2>
          <p class="text-sm text-slate-500 mt-0.5">Informasi lengkap data anggota ZAWA</p>
        </div>
      </div>

      <!-- Placeholder -->
      <div class="bg-white border border-slate-200 rounded-2xl shadow-sm flex flex-col items-center justify-center py-32 text-slate-400">
        <i class="pi pi-user text-5xl mb-4 opacity-20"></i>
        <p class="text-sm font-medium">Halaman detail anggota</p>
        <p class="text-xs mt-1 opacity-70">Konten akan ditambahkan segera</p>
      </div>

    </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from '@/components/layout/AppLayout.vue'
import Button    from 'primevue/button'
import { useRoute } from 'vue-router'

const route = useRoute()
// NIK tersedia di route.params.nik untuk kebutuhan pengembangan selanjutnya
</script>
