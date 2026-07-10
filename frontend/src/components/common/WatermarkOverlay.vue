<template>
  <!-- Watermark overlay: pointer-events none agar tidak mengganggu interaksi -->
  <div class="watermark-overlay" aria-hidden="true">
    <div class="watermark-content">
      <span
        v-for="i in repeatCount"
        :key="i"
        class="watermark-text"
      >
        DO NOT COPY &nbsp;&bull;&nbsp; {{ userEmail }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore  = useAuthStore()
const userEmail  = computed(() => authStore.user?.email || authStore.user?.username || 'CONFIDENTIAL')

// Jumlah pengulangan teks agar memenuhi seluruh area layar
const repeatCount = 60
</script>

<style scoped>
.watermark-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  pointer-events: none;
  overflow: hidden;
  user-select: none;
  -webkit-user-select: none;
}

.watermark-content {
  position: absolute;
  /* Diperlebar agar setelah rotasi tetap memenuhi viewport */
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  gap: 0;
  transform: rotate(-35deg);
  transform-origin: center center;
}

.watermark-text {
  display: inline-block;
  width: 50%;
  padding: 28px 0;
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(15, 23, 42, 0.055);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: clip;
  /* Anti-screenshot: slight blur agar masih terbaca di screenshot tapi blur jika di-crop ketat */
  /* filter: blur(0.2px); */
}

/* Dark mode: sedikit lebih terang karena background gelap */
@media (prefers-color-scheme: dark) {
  .watermark-text {
    color: rgba(255, 255, 255, 0.06);
  }
}
</style>
