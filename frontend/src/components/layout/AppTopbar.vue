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
    <div class="flex items-center gap-3">
      <!-- Nama user -->
      <div class="hidden sm:flex flex-col items-end leading-tight">
        <span class="text-sm font-semibold text-gray-800">{{ auth.userDisplayName }}</span>
        <span class="text-xs text-gray-400 capitalize">{{ auth.user?.user_type === 'dtsen' ? 'LAZ / DTSEN' : 'Internal' }}</span>
      </div>

      <Button icon="pi pi-bell" text rounded severity="secondary" badge="3" badge-severity="danger" />

      <Button
        icon="pi pi-sign-out"
        text
        rounded
        severity="secondary"
        v-tooltip.bottom="'Keluar'"
        @click="confirmVisible = true"
      />
    </div>
  </header>

  <!-- Konfirmasi Logout -->
  <Dialog
    v-model:visible="confirmVisible"
    modal
    :closable="true"
    :style="{ width: '360px' }"
    header="Konfirmasi Keluar"
    :draggable="false"
  >
    <div class="flex flex-col items-center gap-4 py-2">
      <div class="w-14 h-14 rounded-full bg-red-50 flex items-center justify-center">
        <i class="pi pi-sign-out text-red-500" style="font-size: 1.5rem;"></i>
      </div>
      <div class="text-center">
        <p class="text-gray-800 font-semibold mb-1">Yakin ingin keluar?</p>
        <p class="text-gray-500 text-sm">Sesi Anda akan diakhiri dan Anda perlu login kembali.</p>
      </div>
    </div>

    <template #footer>
      <div class="flex gap-2 justify-end">
        <Button
          label="Batal"
          severity="secondary"
          text
          @click="confirmVisible = false"
        />
        <Button
          label="Ya, Keluar"
          severity="danger"
          icon="pi pi-sign-out"
          :loading="loggingOut"
          @click="handleLogout"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button     from 'primevue/button'
import Breadcrumb from 'primevue/breadcrumb'
import Dialog     from 'primevue/dialog'
import { useAuthStore } from '@/stores/auth'

defineEmits(['toggle-sidebar'])

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()

const confirmVisible = ref(false)
const loggingOut     = ref(false)

const breadcrumbHome  = { icon: 'pi pi-home', to: '/dashboard' }
const breadcrumbItems = computed(() => {
  const segments = route.path.split('/').filter(Boolean)
  return segments.map(seg => ({ label: seg.charAt(0).toUpperCase() + seg.slice(1) }))
})

async function handleLogout() {
  loggingOut.value = true
  try {
    await auth.logout()
    router.push({ name: 'home' })
  } finally {
    loggingOut.value     = false
    confirmVisible.value = false
  }
}
</script>
