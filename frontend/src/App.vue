<template>
  <router-view />
  <LoginModal :visible="loginModal.visible" @close="loginModal.close()" />

  <!-- Toast global — digunakan oleh useViewGuard dan komponen lain -->
  <Toast position="top-right" />
</template>

<script setup>
import Toast             from 'primevue/toast'
import { useToast }      from 'primevue/usetoast'
import LoginModal        from '@/components/common/LoginModal.vue'
import { useLoginModalStore } from '@/stores/loginModal'

const loginModal = useLoginModalStore()
const toast      = useToast()

/**
 * Bridge: useViewGuard.js berjalan di luar Vue context (sebelum app.mount),
 * sehingga ia tidak bisa langsung memanggil useToast().
 * Solusinya: viewGuard dispatch CustomEvent 'vg:blocked',
 * dan komponen ini mendengarkan lalu meneruskan ke PrimeVue Toast.
 */
window.addEventListener('vg:blocked', (e) => {
  toast.add({
    severity: 'warn',
    summary:  'Aksi Dilarang',
    detail:   e.detail?.message ?? 'Tindakan ini tidak diizinkan pada halaman ini.',
    life:     3000,
  })
})
</script>

<style>
/* tidak ada global style di sini — semua di assets/main.css */
</style>
