<template>
  <header class="flex items-center justify-between px-6 py-3 bg-white border-b border-gray-200 shadow-sm">
    <!-- Left: toggle + breadcrumb -->
    <div class="flex items-center gap-4">
      <Button
        icon="pi pi-bars"
        text
        rounded
        severity="secondary"
        @click="$emit('toggle-sidebar')"
      />
      <Breadcrumb :home="breadcrumbHome" :model="breadcrumbItems" class="text-sm" />
    </div>

    <!-- Right: actions -->
    <div class="flex items-center gap-2">
      <Button icon="pi pi-bell" text rounded severity="secondary" badge="3" badge-severity="danger" />
      <Button
        icon="pi pi-sign-out"
        text
        rounded
        severity="secondary"
        v-tooltip.bottom="'Keluar'"
        @click="handleLogout"
      />
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import Breadcrumb from 'primevue/breadcrumb'
import { useAuthStore } from '@/stores/auth'

defineEmits(['toggle-sidebar'])

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const breadcrumbHome = { icon: 'pi pi-home', to: '/dashboard' }
const breadcrumbItems = computed(() => {
  const segments = route.path.split('/').filter(Boolean)
  return segments.map(seg => ({ label: seg.charAt(0).toUpperCase() + seg.slice(1) }))
})

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>
