<template>
  <!-- Tampilkan MaintenanceView jika maintenance aktif -->
  <MaintenanceView v-if="maintenanceStore.isMaintenance" />

  <!-- Loading awal saat cek maintenance belum selesai -->
  <div v-else-if="!maintenanceStore.checked" class="app-loading">
    <span class="spinner" />
  </div>

  <!-- Aplikasi normal -->
  <RouterView v-else />
</template>

<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useMaintenanceStore } from '@/stores/maintenance'
import MaintenanceView from '@/views/MaintenanceView.vue'

const maintenanceStore = useMaintenanceStore()

// Cek status maintenance saat pertama kali app di-mount
onMounted(() => {
  maintenanceStore.check()
})
</script>

<style scoped>
.app-loading {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  display: block;
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #2d7dd2;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
