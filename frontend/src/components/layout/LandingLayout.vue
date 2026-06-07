<template>
  <div class="min-h-screen flex flex-col bg-white">
    <LandingNavbar />
    <main class="flex-1">
      <slot />
    </main>
    <LandingFooter />
  </div>
</template>

<script setup>
import LandingNavbar from './LandingNavbar.vue'
import LandingFooter from './LandingFooter.vue'
</script>
