<template>
  <div class="min-h-screen flex flex-col" style="font-family: Inter, sans-serif;">
    <!-- Fixed Navbar -->
    <LandingNavbar />

    <!-- Page sections (navbar is fixed, so no padding-top needed on sections themselves
         except the first hero which handles its own pt) -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- Footer -->
    <LandingFooter />
  </div>
</template>

<script setup>
import LandingNavbar from './LandingNavbar.vue'
import LandingFooter from './LandingFooter.vue'
</script>
