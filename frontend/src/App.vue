<template>
  <router-view />
</template>

<script setup>
// App.vue sengaja kosong — layout ditangani oleh masing-masing route wrapper:
// - LandingLayout  → halaman publik (/, /about, dst)
// - AppLayout      → halaman dashboard (butuh auth)
// - AuthLayout     → halaman login/register
</script>

<style>
/* tidak ada global style di sini — semua di assets/main.css */
</style>
