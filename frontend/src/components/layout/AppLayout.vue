<template>
  <div class="flex h-screen overflow-hidden bg-gray-50">
    <!-- Sidebar -->
    <AppSidebar :collapsed="sidebarCollapsed" />

    <!-- Main area -->
    <div class="flex flex-col flex-1 overflow-hidden">
      <!-- Topbar -->
      <AppTopbar @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed" />

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppSidebar from './AppSidebar.vue'
import AppTopbar from './AppTopbar.vue'

const sidebarCollapsed = ref(false)
</script>
