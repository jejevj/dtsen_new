<template>
  <!-- Watermark overlay: pointer-events none agar tidak mengganggu interaksi -->
  <div
    aria-hidden="true"
    style="
      position: fixed !important;
      inset: 0 !important;
      z-index: 99999 !important;
      pointer-events: none !important;
      overflow: hidden !important;
      user-select: none !important;
      -webkit-user-select: none !important;
      width: 100vw !important;
      height: 100vh !important;
    "
  >
    <div
      style="
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        display: flex;
        flex-wrap: wrap;
        align-content: flex-start;
        transform: rotate(-35deg);
        transform-origin: center center;
      "
    >
      <div
        v-for="i in repeatCount"
        :key="i"
        style="
          display: block;
          width: 50%;
          padding: 32px 0;
          text-align: center;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          color: rgba(15, 23, 42, 0.12);
          white-space: nowrap;
          overflow: hidden;
          font-family: Inter, sans-serif;
          line-height: 1;
        "
      >
        DO NOT COPY &nbsp;&bull;&nbsp; {{ userEmail }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore   = useAuthStore()
const userEmail   = computed(() => authStore.user?.email || authStore.user?.username || 'CONFIDENTIAL')
const repeatCount = 80
</script>
