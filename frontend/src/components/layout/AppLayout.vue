<template>
  <!-- Full-screen app shell -->
  <div class="flex h-screen w-screen overflow-hidden bg-slate-50" style="font-family: Inter, sans-serif;">

    <!-- ===== SIDEBAR ===== -->
    <aside
      :class="[
        'flex-shrink-0 flex flex-col bg-primary-900 transition-all duration-300 ease-in-out overflow-hidden',
        sidebarOpen ? 'w-60' : 'w-16'
      ]"
    >
      <!-- Logo -->
      <div class="flex items-center h-16 px-4 border-b border-primary-800 gap-3 flex-shrink-0">
        <div class="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center flex-shrink-0">
          <i class="pi pi-chart-bar text-white" style="font-size: 0.8rem"></i>
        </div>
        <transition name="fade">
          <div v-if="sidebarOpen" class="overflow-hidden whitespace-nowrap">
            <div class="font-bold text-white text-sm tracking-tight leading-none">DTSEN</div>
            <div class="text-green-400 text-[10px] leading-none mt-0.5">Zakat &amp; Wakaf</div>
          </div>
        </transition>
      </div>

      <!-- Nav items -->
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

        <!-- Divider -->
        <div class="my-3 mx-3 border-t border-primary-800"></div>

        <!-- Secondary items -->
        <ul class="space-y-0.5 px-2">
          <li v-for="item in secondaryItems" :key="item.to">
            <router-link
              :to="item.to"
              v-tooltip.right="!sidebarOpen ? item.label : null"
              :class="[
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all group',
                isActive(item.to)
                  ? 'bg-primary-700 text-white'
                  : 'text-primary-400 hover:bg-primary-800 hover:text-white'
              ]"
            >
              <i :class="[item.icon, 'flex-shrink-0 w-4 text-center text-base']"></i>
              <transition name="fade">
                <span v-if="sidebarOpen" class="whitespace-nowrap overflow-hidden">{{ item.label }}</span>
              </transition>
            </router-link>
          </li>
        </ul>
      </nav>

      <!-- User section -->
      <div class="flex-shrink-0 border-t border-primary-800 p-3">
        <div
          :class="['flex items-center gap-3 p-2 rounded-xl hover:bg-primary-800 cursor-pointer transition-colors', !sidebarOpen && 'justify-center']">
          <Avatar
            :label="userInitials"
            shape="circle"
            class="flex-shrink-0 bg-primary-600 text-white font-semibold"
            style="width: 32px; height: 32px; font-size: 0.75rem"
          />
          <transition name="fade">
            <div v-if="sidebarOpen" class="overflow-hidden">
              <p class="text-sm font-medium text-white truncate leading-none">{{ user?.name || 'Admin' }}</p>
              <p class="text-[11px] text-primary-400 truncate mt-0.5">{{ user?.email || '' }}</p>
            </div>
          </transition>
        </div>
      </div>
    </aside>

    <!-- ===== MAIN AREA ===== -->
    <div class="flex flex-col flex-1 min-w-0 overflow-hidden">

      <!-- Topbar -->
      <header class="flex-shrink-0 flex items-center justify-between h-16 px-4 bg-white border-b border-slate-200 shadow-sm gap-4">
        <!-- Left -->
        <div class="flex items-center gap-3">
          <Button
            :icon="sidebarOpen ? 'pi pi-align-left' : 'pi pi-align-right'"
            text rounded
            class="text-slate-500 hover:text-primary-700 hover:bg-primary-50 w-9 h-9"
            @click="sidebarOpen = !sidebarOpen"
          />
          <!-- Breadcrumb -->
          <div class="hidden sm:flex items-center gap-1.5 text-sm">
            <span class="text-slate-400">DTSEN</span>
            <i class="pi pi-angle-right text-slate-300" style="font-size: 0.7rem"></i>
            <span class="font-medium text-slate-700">{{ currentPageLabel }}</span>
          </div>
        </div>

        <!-- Right -->
        <div class="flex items-center gap-1">
          <!-- Search -->
          <Button icon="pi pi-search" text rounded class="text-slate-500 hover:text-primary-700 hover:bg-primary-50 w-9 h-9" />
          <!-- Notification -->
          <div class="relative">
            <Button icon="pi pi-bell" text rounded class="text-slate-500 hover:text-primary-700 hover:bg-primary-50 w-9 h-9" />
            <span class="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-red-500"></span>
          </div>
          <!-- Divider -->
          <div class="w-px h-6 bg-slate-200 mx-1"></div>
          <!-- User pill -->
          <div class="flex items-center gap-2 pl-1 pr-3 py-1.5 rounded-full hover:bg-slate-100 cursor-pointer transition-colors" @click="showUserMenu = !showUserMenu">
            <Avatar
              :label="userInitials"
              shape="circle"
              class="bg-primary-600 text-white font-semibold"
              style="width: 28px; height: 28px; font-size: 0.7rem"
            />
            <span class="hidden sm:block text-sm font-medium text-slate-700">{{ user?.name?.split(' ')[0] || 'Admin' }}</span>
            <i class="pi pi-angle-down text-slate-400" style="font-size: 0.65rem"></i>
          </div>

          <!-- User dropdown -->
          <div
            v-if="showUserMenu"
            class="absolute top-14 right-4 w-48 bg-white rounded-xl shadow-lg border border-slate-100 py-1 z-50"
            @mouseleave="showUserMenu = false"
          >
            <div class="px-4 py-2.5 border-b border-slate-100">
              <p class="text-sm font-semibold text-slate-800">{{ user?.name || 'Admin' }}</p>
              <p class="text-xs text-slate-400 truncate">{{ user?.email }}</p>
            </div>
            <button class="w-full flex items-center gap-2.5 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 transition-colors">
              <i class="pi pi-user text-xs text-slate-400"></i> Profil Saya
            </button>
            <button class="w-full flex items-center gap-2.5 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 transition-colors">
              <i class="pi pi-cog text-xs text-slate-400"></i> Pengaturan
            </button>
            <div class="border-t border-slate-100 mt-1"></div>
            <button
              class="w-full flex items-center gap-2.5 px-4 py-2 text-sm text-red-500 hover:bg-red-50 transition-colors"
              @click="logout"
            >
              <i class="pi pi-sign-out text-xs"></i> Keluar
            </button>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto p-5">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'
import { useAuthStore } from '@/stores/auth'

const route       = useRoute()
const router      = useRouter()
const authStore   = useAuthStore()
const sidebarOpen = ref(true)
const showUserMenu = ref(false)

const user = computed(() => authStore.user)
const userInitials = computed(() => {
  const name = user.value?.name || 'Admin'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const navItems = [
  { to: '/dashboard', label: 'Dashboard',      icon: 'pi pi-home' },
  { to: '/mustahik',  label: 'Data Mustahik',  icon: 'pi pi-users' },
  { to: '/report',    label: 'Laporan',         icon: 'pi pi-chart-line' },
]
const secondaryItems = [
  { to: '/laz',       label: 'Data LAZ',        icon: 'pi pi-building' },
]

const pageLabels = {
  '/dashboard': 'Dashboard',
  '/mustahik':  'Data Mustahik',
  '/report':    'Laporan',
  '/laz':       'Data LAZ',
}
const currentPageLabel = computed(() => pageLabels[route.path] || 'Halaman')

function isActive(to) {
  return route.path === to || route.path.startsWith(to + '/')
}

function logout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
