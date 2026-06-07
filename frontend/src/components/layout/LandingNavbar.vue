<template>
  <!-- class 'landing-nav' dipakai CSS global untuk force fixed position -->
  <nav
    class="landing-nav"
    :style="{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 9999,
      transition: 'background 0.3s, box-shadow 0.3s',
      background: scrolled ? 'rgba(255,255,255,0.97)' : 'transparent',
      backdropFilter: scrolled ? 'blur(12px)' : 'none',
      borderBottom: scrolled ? '1px solid #f1f5f9' : 'none',
      boxShadow: scrolled ? '0 1px 8px 0 rgba(0,0,0,0.07)' : 'none'
    }"
  >
    <div style="max-width:1280px; margin:0 auto; padding:0 1.5rem;">
      <div style="display:flex; align-items:center; justify-content:space-between; height:64px;">

        <!-- Logo -->
        <router-link to="/" style="display:flex; align-items:center; gap:10px; text-decoration:none;">
          <div style="width:34px; height:34px; border-radius:10px; background:#16a34a; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
            <i class="pi pi-chart-bar" style="color:white; font-size:14px;"></i>
          </div>
          <div style="line-height:1;">
            <div :style="{ fontWeight: 700, fontSize: '15px', letterSpacing: '-0.02em', color: scrolled ? '#15803d' : '#ffffff', transition: 'color 0.3s' }">
              DTSEN
            </div>
            <div :style="{ fontSize: '10px', color: scrolled ? '#94a3b8' : '#bbf7d0', transition: 'color 0.3s', marginTop:'2px' }">
              Zakat &amp; Wakaf
            </div>
          </div>
        </router-link>

        <!-- Desktop menu -->
        <div class="hide-mobile" style="display:flex; align-items:center; gap:4px;">
          <a
            v-for="item in navItems"
            :key="item.label"
            :href="item.href"
            :style="{
              padding: '6px 14px',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 500,
              textDecoration: 'none',
              transition: 'background 0.2s, color 0.2s',
              color: scrolled ? '#475569' : 'rgba(255,255,255,0.9)',
            }"
            @mouseenter="e => e.target.style.background = scrolled ? '#f0fdf4' : 'rgba(255,255,255,0.12)'"
            @mouseleave="e => e.target.style.background = 'transparent'"
          >
            {{ item.label }}
          </a>
        </div>

        <!-- Right: Login + Hamburger -->
        <div style="display:flex; align-items:center; gap:8px;">
          <!-- Login button -->
          <button
            class="hide-mobile"
            :style="{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '7px 18px',
              borderRadius: '8px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
              border: scrolled ? '1.5px solid #16a34a' : '1.5px solid rgba(255,255,255,0.6)',
              background: scrolled ? '#16a34a' : 'rgba(255,255,255,0.15)',
              color: scrolled ? '#ffffff' : '#ffffff',
            }"
            @click="$router.push('/login')"
          >
            <i class="pi pi-sign-in" style="font-size:12px;"></i>
            Masuk
          </button>

          <!-- Hamburger (mobile) -->
          <button
            class="show-mobile"
            style="width:36px;height:36px;border-radius:8px;border:none;cursor:pointer;display:none;align-items:center;justify-content:center;"
            :style="{ background: scrolled ? '#f1f5f9' : 'rgba(255,255,255,0.15)' }"
            @click="mobileOpen = !mobileOpen"
          >
            <i :class="mobileOpen ? 'pi pi-times' : 'pi pi-bars'" :style="{ color: scrolled ? '#475569' : '#ffffff', fontSize:'15px' }"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile dropdown -->
    <div
      v-if="mobileOpen"
      style="background:white; border-top:1px solid #f1f5f9; box-shadow:0 8px 24px rgba(0,0,0,0.1);"
    >
      <div style="padding:12px 16px;">
        <a
          v-for="item in navItems"
          :key="item.label"
          :href="item.href"
          style="display:flex; align-items:center; gap:10px; padding:10px 12px; border-radius:8px; font-size:14px; font-weight:500; color:#374151; text-decoration:none; margin-bottom:2px;"
          @click="mobileOpen = false"
        >
          <i :class="item.icon" style="font-size:13px; color:#16a34a; width:16px; text-align:center;"></i>
          {{ item.label }}
        </a>
        <div style="padding:8px 0 4px;">
          <button
            style="width:100%; padding:10px; border-radius:8px; background:#16a34a; color:white; border:none; font-size:14px; font-weight:600; cursor:pointer;"
            @click="$router.push('/login')"
          >
            Masuk ke Sistem
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const scrolled   = ref(false)
const mobileOpen = ref(false)

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
onMounted(()  => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
@media (max-width: 768px) {
  .hide-mobile { display: none !important; }
  .show-mobile { display: flex !important; }
}
</style>
