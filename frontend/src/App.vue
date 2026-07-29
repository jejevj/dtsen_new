<template>
  <!-- Tampilkan MaintenanceView jika maintenance aktif -->
  <MaintenanceView v-if="maintenanceStore.isMaintenance" />

  <!-- Loading awal saat cek maintenance belum selesai -->
  <div v-else-if="!maintenanceStore.checked" class="app-loading">
    <span class="spinner" />
  </div>

  <!-- Aplikasi normal -->
  <template v-else>
    <RouterView />
    <!-- Modal login global: dipasang di sini agar bisa dipanggil dari mana saja -->
    <LoginModal :visible="loginModal.visible" @close="loginModal.close()" />
  </template>
</template>

<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useMaintenanceStore }  from '@/stores/maintenance'
import { useLoginModalStore }   from '@/stores/loginModal'
import MaintenanceView from '@/views/MaintenanceView.vue'
import LoginModal      from '@/components/common/LoginModal.vue'

const maintenanceStore = useMaintenanceStore()
const loginModal       = useLoginModalStore()

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
