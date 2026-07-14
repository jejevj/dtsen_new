<template>
  <aside
    :class="[
      'flex flex-col bg-primary-800 text-white transition-all duration-300 ease-in-out',
      collapsed ? 'w-16' : 'w-64'
    ]"
  >
    <!-- Logo -->
    <div class="flex items-center gap-3 px-4 py-5 border-b border-primary-700">
      <i class="pi pi-chart-bar text-secondary text-2xl"></i>
      <span v-if="!collapsed" class="font-bold text-lg tracking-tight">DTSEN</span>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 py-4">
      <ul class="space-y-1 px-2">
        <li v-for="item in menuItems" :key="item.to">
          <router-link
            :to="item.to"
            v-tooltip.right="collapsed ? item.label : null"
            class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors"
            :class="[
              $route.path === item.to
                ? 'bg-primary-600 text-white'
                : 'text-primary-200 hover:bg-primary-700 hover:text-white'
            ]"
          >
            <i :class="[item.icon, 'text-base w-5 text-center']"></i>
            <span v-if="!collapsed">{{ item.label }}</span>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- User info -->
    <div v-if="!collapsed" class="px-4 py-4 border-t border-primary-700">
      <div class="flex items-center gap-3">
        <Avatar :label="userInitials" shape="circle" class="bg-secondary text-white" />
        <div class="overflow-hidden">
          <p class="text-sm font-medium truncate">{{ user?.name || 'Admin' }}</p>
          <p class="text-xs text-primary-300 truncate">{{ user?.email }}</p>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import Avatar from 'primevue/avatar'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  collapsed: { type: Boolean, default: false }
})

const authStore = useAuthStore()
const user = computed(() => authStore.user)
const userInitials = computed(() => {
  if (!user.value?.name) return 'A'
  return user.value.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const menuItems = [
  { to: '/dashboard',  label: 'Dashboard',         icon: 'pi pi-home' },
  { to: '/mustahik',   label: 'Data Mustahik',     icon: 'pi pi-users' },
  { to: '/laporan',    label: 'Pemeriksaan DTSEN', icon: 'pi pi-file-check' },
]
</script>
