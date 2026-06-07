<template>
  <nav
    :class="[
      'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
      scrolled
        ? 'bg-white/95 backdrop-blur-md border-b border-gray-100 shadow-sm'
        : 'bg-transparent'
    ]"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">

        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-2.5 no-underline group">
          <div class="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center shadow-sm">
            <i class="pi pi-chart-bar text-white" style="font-size: 0.875rem"></i>
          </div>
          <div class="leading-none">
            <div :class="['font-bold text-base tracking-tight transition-colors', scrolled ? 'text-primary-700' : 'text-white']">
              DTSEN
            </div>
            <div :class="['text-[10px] transition-colors', scrolled ? 'text-gray-400' : 'text-green-200']">
              Zakat &amp; Wakaf
            </div>
          </div>
        </router-link>

        <!-- Desktop menu -->
        <div class="hidden md:flex items-center gap-1">
          <a
            v-for="item in navItems"
            :key="item.label"
            :href="item.href"
            :class="[
              'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
              scrolled
                ? 'text-gray-600 hover:text-primary-700 hover:bg-primary-50'
                : 'text-green-100 hover:text-white hover:bg-white/10'
            ]"
          >
            {{ item.label }}
          </a>
        </div>

        <!-- CTA -->
        <div class="flex items-center gap-2">
          <!-- Mobile hamburger -->
          <Button
            icon="pi pi-bars"
            text rounded
            :class="['md:hidden', scrolled ? 'text-gray-700' : 'text-white']"
            @click="mobileOpen = !mobileOpen"
          />
          <!-- Login button -->
          <Button
            label="Masuk"
            icon="pi pi-sign-in"
            size="small"
            :class="[
              'hidden md:inline-flex transition-all',
              scrolled
                ? 'bg-primary-600 border-primary-600 text-white hover:bg-primary-700'
                : 'bg-white/15 border-white/40 text-white hover:bg-white/25'
            ]"
            @click="$router.push('/login')"
          />
        </div>
      </div>
    </div>

    <!-- Mobile dropdown -->
    <transition name="slide-down">
      <div
        v-if="mobileOpen"
        class="md:hidden bg-white border-t border-gray-100 shadow-lg"
      >
        <div class="px-4 py-3 space-y-1">
          <a
            v-for="item in navItems"
            :key="item.label"
            :href="item.href"
            class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-primary-50 hover:text-primary-700"
            @click="mobileOpen = false"
          >
            <i :class="item.icon + ' text-primary-500 w-4 text-center'"></i>
            {{ item.label }}
          </a>
          <div class="pt-2 pb-1">
            <Button
              label="Masuk ke Sistem"
              icon="pi pi-sign-in"
              class="w-full bg-primary-600 border-primary-600 text-white"
              @click="$router.push('/login')"
            />
          </div>
        </div>
      </div>
    </transition>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Button from 'primevue/button'

const scrolled    = ref(false)
const mobileOpen  = ref(false)

const navItems = [
  { label: 'Beranda',   href: '#hero',    icon: 'pi pi-home' },
  { label: 'Statistik', href: '#stats',   icon: 'pi pi-chart-bar' },
  { label: 'Peta',      href: '#map',     icon: 'pi pi-map' },
  { label: 'Program',   href: '#program', icon: 'pi pi-list' },
  { label: 'Tentang',   href: '#tentang', icon: 'pi pi-info-circle' },
]

function onScroll() {
  scrolled.value = window.scrollY > 50
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.2s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
