<template>
  <div class="flex h-screen w-screen overflow-hidden bg-slate-50" style="font-family: Inter, sans-serif;">

    <!-- ===== SIDEBAR ===== -->
    <aside
      :class="[
        'flex-shrink-0 flex flex-col bg-primary-900 transition-all duration-300 ease-in-out overflow-hidden',
        sidebarOpen ? 'w-60' : 'w-16'
      ]"
    >
      <div class="flex items-center h-16 px-4 border-b border-primary-800 gap-3 flex-shrink-0">
        <img
          src="https://simzat.kemenag.go.id/simzat/apps/assets/images/ico.png"
          alt="DTSEN Logo"
          class="flex-shrink-0"
          style="width:32px;height:32px;border-radius:8px;object-fit:contain;"
        />
        <transition name="fade">
          <div v-if="sidebarOpen" class="overflow-hidden whitespace-nowrap">
            <div class="font-bold text-white text-sm tracking-tight leading-none">DTSEN</div>
            <div class="text-green-400 text-[10px] leading-none mt-0.5">Zakat</div>
          </div>
        </transition>
      </div>

      <nav class="flex-1 py-3 overflow-y-auto overflow-x-hidden">
        <ul class="space-y-0.5 px-2">
          <li v-for="item in navItems" :key="item.to">
            <router-link
              :to="item.to"
              v-tooltip.right="!sidebarOpen ? item.label : null"
              :class="[
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all group',
                isActive(item.to)
                  ? 'bg-primary-700 text-white shadow-sm'
                  : 'text-primary-300 hover:bg-primary-800 hover:text-white'
              ]"
            >
              <i :class="[item.icon, 'flex-shrink-0 w-4 text-center text-base', isActive(item.to) ? 'text-green-300' : 'text-primary-400 group-hover:text-green-300']"></i>
              <transition name="fade">
                <span v-if="sidebarOpen" class="whitespace-nowrap overflow-hidden">{{ item.label }}</span>
              </transition>
            </router-link>
          </li>
        </ul>
      </nav>

      <div class="flex-shrink-0 border-t border-primary-800 p-3">
        <div :class="['flex items-center gap-3 p-2 rounded-xl hover:bg-primary-800 cursor-pointer transition-colors', !sidebarOpen && 'justify-center']">
          <Avatar
            :label="userInitials"
            shape="circle"
            class="flex-shrink-0 bg-primary-600 text-white font-semibold"
            style="width: 32px; height: 32px; font-size: 0.75rem"
          />
          <transition name="fade">
            <div v-if="sidebarOpen" class="overflow-hidden">
              <p class="text-sm font-medium text-white truncate leading-none">{{ userDisplayName }}</p>
              <p class="text-[11px] text-primary-400 truncate mt-0.5">{{ userTypeLabel }}</p>
            </div>
          </transition>
        </div>
      </div>
    </aside>

    <!-- ===== MAIN AREA ===== -->
    <div class="flex flex-col flex-1 min-w-0 overflow-hidden">

      <!-- Topbar -->
      <header class="flex-shrink-0 flex items-center justify-between h-16 px-4 bg-white border-b border-slate-200 shadow-sm gap-4">
        <div class="flex items-center gap-3">
          <Button
            :icon="sidebarOpen ? 'pi pi-align-left' : 'pi pi-align-right'"
            text rounded
            class="text-slate-500 hover:text-primary-700 hover:bg-primary-50 w-9 h-9"
            @click="sidebarOpen = !sidebarOpen"
          />
          <div class="hidden sm:flex items-center gap-1.5 text-sm">
            <span class="text-slate-400">DTSEN</span>
            <i class="pi pi-angle-right text-slate-300" style="font-size: 0.7rem"></i>
            <span class="font-medium text-slate-700">{{ currentPageLabel }}</span>
          </div>
        </div>

        <div class="flex items-center gap-1">
          <div class="w-px h-6 bg-slate-200 mx-1"></div>
          <div
            class="flex items-center gap-2 pl-1 pr-3 py-1.5 rounded-full hover:bg-slate-100 cursor-pointer transition-colors"
            @click="showUserMenu = !showUserMenu"
          >
            <Avatar
              :label="userInitials"
              shape="circle"
              class="bg-primary-600 text-white font-semibold"
              style="width: 28px; height: 28px; font-size: 0.7rem"
            />
            <span class="hidden sm:block text-sm font-medium text-slate-700">{{ userFirstName }}</span>
            <i class="pi pi-angle-down text-slate-400" style="font-size: 0.65rem"></i>
          </div>

          <!-- User dropdown -->
          <div
            v-if="showUserMenu"
            class="absolute top-14 right-4 w-52 bg-white rounded-xl shadow-lg border border-slate-100 py-1 z-50"
            @mouseleave="showUserMenu = false"
          >
            <div class="px-4 py-2.5 border-b border-slate-100">
              <p class="text-sm font-semibold text-slate-800">{{ userDisplayName }}</p>
              <p class="text-xs text-slate-400 truncate">{{ userTypeLabel }}</p>
            </div>
            <div class="border-t border-slate-100 mt-1"></div>
            <button
              class="w-full flex items-center gap-2.5 px-4 py-2 text-sm text-red-500 hover:bg-red-50 transition-colors"
              @click="showUserMenu = false; confirmVisible = true"
            >
              <i class="pi pi-sign-out text-xs"></i> Keluar
            </button>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto p-5 wm-main">

        <!-- ===== WATERMARK SVG PATTERN ===== -->
        <div class="wm-overlay" aria-hidden="true">
          <svg class="wm-svg" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern
                id="app-wm"
                x="0" y="0"
                width="320" height="120"
                patternUnits="userSpaceOnUse"
                patternTransform="rotate(-35)"
              >
                <text x="10" y="40"
                  font-family="Inter, sans-serif"
                  font-size="11"
                  font-weight="700"
                  letter-spacing="2"
                  fill="rgba(15,23,42,0.09)"
                  text-anchor="start"
                >DO NOT COPY</text>
                <text x="10" y="68"
                  font-family="Inter, sans-serif"
                  font-size="10"
                  font-weight="600"
                  letter-spacing="1"
                  fill="rgba(15,23,42,0.07)"
                  text-anchor="start"
                >{{ userIdentifier }}</text>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#app-wm)" />
          </svg>
        </div>
        <!-- ===== END WATERMARK ===== -->

        <div class="wm-content">
          <slot />
        </div>
      </main>
    </div>
  </div>

  <!-- ===== DIALOG KONFIRMASI LOGOUT ===== -->
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
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'
import Dialog from 'primevue/dialog'
import { useAuthStore } from '@/stores/auth'

const route      = useRoute()
const router     = useRouter()
const authStore  = useAuthStore()

const sidebarOpen    = ref(true)
const showUserMenu   = ref(false)
const confirmVisible = ref(false)
const loggingOut     = ref(false)

const user = computed(() => authStore.user)

const userIdentifier = computed(() => {
  const u = user.value
  if (!u) return 'CONFIDENTIAL'
  return u.email || u.tuser_email || u.notelp || u.username || u.user_id || 'CONFIDENTIAL'
})

const userDisplayName = computed(() => authStore.userDisplayName || 'Admin')
const userFirstName   = computed(() => userDisplayName.value.split(' ')[0])
const userTypeLabel   = computed(() =>
  user.value?.user_type === 'dtsen' ? 'LAZ / DTSEN' : 'Internal'
)
const userInitials = computed(() =>
  userDisplayName.value.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
)

const navItems = [
  { to: '/dashboard', label: 'Dashboard',         icon: 'pi pi-home' },
  { to: '/mustahik',  label: 'Data Penerima Manfaat',     icon: 'pi pi-users' },
  { to: '/report',    label: 'Pemeriksaan DTSEN', icon: 'pi pi-chart-line' },
]

const pageLabels = {
  '/dashboard': 'Dashboard',
  '/mustahik':  'Data Mustahik',
  '/report':    'Pemeriksaan DTSEN',
}
const currentPageLabel = computed(() => pageLabels[route.path] || 'Halaman')

function isActive(to) {
  return route.path === to || route.path.startsWith(to + '/')
}

async function handleLogout() {
  loggingOut.value = true
  try {
    await authStore.logout()
    router.push({ name: 'home' })
  } finally {
    loggingOut.value     = false
    confirmVisible.value = false
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.wm-main { position: relative; }

.wm-overlay {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  user-select: none;
  -webkit-user-select: none;
  height: 100%;
  min-height: 100%;
}
.wm-svg {
  display: block;
  width: 100%;
  height: 100%;
  min-height: 100%;
}

.wm-content {
  position: relative;
  z-index: 1;
}
</style>
