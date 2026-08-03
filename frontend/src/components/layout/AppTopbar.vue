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

      <!-- Notifikasi -->
      <Button icon="pi pi-bell" text rounded severity="secondary" badge="3" badge-severity="danger" />

      <!-- Profil dropdown -->
      <div style="position:relative;">
        <button
          @click="profileOpen = !profileOpen"
          style="display:inline-flex;align-items:center;gap:8px;padding:5px 10px 5px 5px;border-radius:99px;border:1px solid #e2e8f0;background:white;cursor:pointer;font-size:13px;transition:background 0.15s;"
        >
          <!-- Avatar initials -->
          <div style="width:28px;height:28px;border-radius:50%;background:#16a34a;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
            <span style="color:white;font-size:11px;font-weight:700;">{{ userInitials }}</span>
          </div>
          <!-- Nama + role (hidden xs) -->
          <div class="hidden sm:flex flex-col items-start leading-tight" style="max-width:140px;">
            <span style="font-size:12px;font-weight:600;color:#1e293b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:130px;">{{ auth.userDisplayName }}</span>
            <span style="font-size:10px;color:#94a3b8;">{{ auth.user?.user_type === 'dtsen' ? 'LAZ / DTSEN' : 'Internal' }}</span>
          </div>
          <i class="pi pi-angle-down" style="font-size:11px;color:#94a3b8;"></i>
        </button>

        <!-- Dropdown menu -->
        <div
          v-if="profileOpen"
          style="position:absolute;right:0;top:calc(100% + 8px);background:white;border:1px solid #e2e8f0;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.10);min-width:196px;overflow:hidden;z-index:200;"
        >
          <!-- Info -->
          <div style="padding:12px 16px;border-bottom:1px solid #f1f5f9;">
            <p style="font-size:12px;font-weight:700;color:#1e293b;margin:0 0 2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{{ auth.userDisplayName }}</p>
            <p style="font-size:11px;color:#94a3b8;margin:0;">{{ auth.user?.email || auth.user?.notelp || '' }}</p>
          </div>

          <!-- Ubah Password -->
          <router-link
            to="/profil"
            style="display:flex;align-items:center;gap:10px;padding:10px 16px;font-size:13px;font-weight:500;color:#374151;text-decoration:none;transition:background 0.15s;"
            active-style="background:#f0fdf4;"
            @click="profileOpen = false"
          >
            <i class="pi pi-lock" style="font-size:13px;color:#f97316;"></i>
            Ubah Password
          </router-link>

          <!-- Keluar -->
          <button
            @click="profileOpen = false; confirmVisible = true"
            style="width:100%;display:flex;align-items:center;gap:10px;padding:10px 16px;font-size:13px;font-weight:500;color:#dc2626;background:transparent;border:none;cursor:pointer;border-top:1px solid #f1f5f9;transition:background 0.15s;"
          >
            <i class="pi pi-sign-out" style="font-size:13px;"></i>
            Keluar
          </button>
        </div>
      </div>
    </div>
  </header>

  <!-- Overlay tutup dropdown -->
  <div
    v-if="profileOpen"
    style="position:fixed;inset:0;z-index:199;"
    @click="profileOpen = false"
  />

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
        <Button label="Batal" severity="secondary" text @click="confirmVisible = false" />
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
const profileOpen    = ref(false)

const userInitials = computed(() => {
  const name = auth.userDisplayName
  if (!name) return 'U'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

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
