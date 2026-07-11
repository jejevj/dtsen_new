<template>
  <nav
    style="
      position: fixed;
      top: 0; left: 0; right: 0;
      z-index: 9999;
      background: rgba(255,255,255,0.98);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid #e2e8f0;
      box-shadow: 0 1px 6px rgba(0,0,0,0.06);
      font-family: Inter, sans-serif;
    "
  >
    <div style="max-width:1280px; margin:0 auto; padding:0 24px; display:flex; align-items:center; justify-content:space-between; height:64px;">

      <!-- Logo -->
      <router-link to="/" style="display:flex; align-items:center; gap:10px; text-decoration:none; flex-shrink:0;">
        <div style="width:34px;height:34px;border-radius:10px;background:#16a34a;display:flex;align-items:center;justify-content:center;">
          <i class="pi pi-chart-bar" style="color:white;font-size:14px;"></i>
        </div>
        <div style="line-height:1;">
          <div style="font-weight:700;font-size:15px;letter-spacing:-0.02em;color:#15803d;">DTSEN</div>
          <div style="font-size:10px;color:#94a3b8;margin-top:2px;">Zakat</div>
        </div>
      </router-link>

      <!-- Desktop menu -->
      <div class="nav-desktop" style="display:flex;align-items:center;gap:2px;">
        <a
          v-for="item in navItems"
          :key="item.label"
          :href="item.href"
          class="nav-link"
          style="padding:7px 14px;border-radius:8px;font-size:13.5px;font-weight:500;color:#475569;text-decoration:none;transition:background 0.15s,color 0.15s;"
        >
          {{ item.label }}
        </a>
      </div>

      <!-- Right -->
      <div style="display:flex;align-items:center;gap:8px;">

        <!-- Belum login: tombol Masuk -->
        <button
          v-if="!authStore.isAuthenticated"
          class="btn-login nav-desktop"
          style="display:inline-flex;align-items:center;gap:6px;padding:8px 18px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;border:none;background:#16a34a;color:#fff;transition:background 0.15s;"
          @click="loginModal.open()"
        >
          <i class="pi pi-sign-in" style="font-size:12px;"></i>
          Masuk
        </button>

        <!-- Sudah login: profil dropdown -->
        <div v-else class="nav-desktop" style="position:relative;">
          <button
            @click="profileOpen = !profileOpen"
            style="display:inline-flex;align-items:center;gap:8px;padding:6px 12px 6px 6px;border-radius:99px;border:1px solid #e2e8f0;background:white;cursor:pointer;font-size:13px;font-weight:600;color:#374151;transition:background 0.15s;"
          >
            <div style="width:28px;height:28px;border-radius:50%;background:#16a34a;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
              <i class="pi pi-user" style="font-size:12px;color:white;"></i>
            </div>
            <span style="max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{{ authStore.userDisplayName || 'Profil' }}</span>
            <i class="pi pi-angle-down" style="font-size:11px;color:#94a3b8;"></i>
          </button>

          <!-- Dropdown -->
          <div
            v-if="profileOpen"
            style="position:absolute;right:0;top:calc(100% + 8px);background:white;border:1px solid #e2e8f0;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.10);min-width:200px;overflow:hidden;z-index:100;"
          >
            <!-- Info user -->
            <div style="padding:14px 16px;border-bottom:1px solid #f1f5f9;">
              <p style="font-size:12px;font-weight:700;color:#1e293b;margin:0 0 2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{{ authStore.userDisplayName }}</p>
              <p style="font-size:11px;color:#94a3b8;margin:0;">{{ authStore.user?.email || authStore.user?.notelp || '' }}</p>
            </div>
            <!-- Ke Dashboard -->
            <router-link
              to="/dashboard"
              style="display:flex;align-items:center;gap:10px;padding:11px 16px;font-size:13px;font-weight:500;color:#374151;text-decoration:none;transition:background 0.15s;"
              @click="profileOpen = false"
            >
              <i class="pi pi-th-large" style="font-size:13px;color:#16a34a;"></i>
              Dashboard
            </router-link>
            <!-- Logout -->
            <button
              @click="handleLogout"
              style="width:100%;display:flex;align-items:center;gap:10px;padding:11px 16px;font-size:13px;font-weight:500;color:#dc2626;background:transparent;border:none;cursor:pointer;border-top:1px solid #f1f5f9;transition:background 0.15s;"
            >
              <i class="pi pi-sign-out" style="font-size:13px;"></i>
              Keluar
            </button>
          </div>
        </div>

        <!-- Hamburger -->
        <button
          class="nav-mobile"
          style="display:none;width:36px;height:36px;border-radius:8px;border:1px solid #e2e8f0;background:#f8fafc;cursor:pointer;align-items:center;justify-content:center;"
          @click="mobileOpen = !mobileOpen"
        >
          <i :class="mobileOpen ? 'pi pi-times' : 'pi pi-bars'" style="font-size:15px;color:#475569;"></i>
        </button>
      </div>
    </div>

    <!-- Mobile dropdown -->
    <div
      v-if="mobileOpen"
      style="background:white;border-top:1px solid #f1f5f9;padding:10px 16px 14px;"
    >
      <a
        v-for="item in navItems"
        :key="item.label"
        :href="item.href"
        style="display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:8px;font-size:14px;font-weight:500;color:#374151;text-decoration:none;margin-bottom:2px;"
        @click="mobileOpen = false"
      >
        <i :class="item.icon" style="font-size:13px;color:#16a34a;width:16px;text-align:center;"></i>
        {{ item.label }}
      </a>

      <!-- Mobile: belum login -->
      <template v-if="!authStore.isAuthenticated">
        <button
          style="margin-top:8px;width:100%;padding:10px;border-radius:8px;background:#16a34a;color:white;border:none;font-size:14px;font-weight:600;cursor:pointer;"
          @click="mobileOpen = false; loginModal.open()"
        >
          Masuk ke Sistem
        </button>
      </template>

      <!-- Mobile: sudah login -->
      <template v-else>
        <div style="margin-top:8px;padding:10px 12px;border-radius:8px;background:#f0fdf4;display:flex;align-items:center;gap:10px;">
          <div style="width:32px;height:32px;border-radius:50%;background:#16a34a;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
            <i class="pi pi-user" style="font-size:13px;color:white;"></i>
          </div>
          <div style="flex:1;min-width:0;">
            <p style="font-size:13px;font-weight:700;color:#15803d;margin:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{{ authStore.userDisplayName }}</p>
            <p style="font-size:11px;color:#64748b;margin:0;">{{ authStore.user?.email || authStore.user?.notelp || '' }}</p>
          </div>
        </div>
        <router-link
          to="/dashboard"
          style="margin-top:6px;width:100%;display:flex;align-items:center;justify-content:center;gap:8px;padding:10px;border-radius:8px;background:#eff6ff;color:#2563eb;font-size:14px;font-weight:600;text-decoration:none;"
          @click="mobileOpen = false"
        >
          <i class="pi pi-th-large" style="font-size:13px;"></i>
          Dashboard
        </router-link>
        <button
          style="margin-top:6px;width:100%;padding:10px;border-radius:8px;background:#fef2f2;color:#dc2626;border:none;font-size:14px;font-weight:600;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;"
          @click="mobileOpen = false; handleLogout()"
        >
          <i class="pi pi-sign-out" style="font-size:13px;"></i>
          Keluar
        </button>
      </template>
    </div>
  </nav>

  <!-- Klik luar dropdown: tutup -->
  <div
    v-if="profileOpen"
    style="position:fixed;inset:0;z-index:98;"
    @click="profileOpen = false"
  />
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useLoginModalStore } from '@/stores/loginModal'
import { useAuthStore }       from '@/stores/auth'

const mobileOpen  = ref(false)
const profileOpen = ref(false)
const loginModal  = useLoginModalStore()
const authStore   = useAuthStore()
const router      = useRouter()

const navItems = [
  { label: 'Beranda',   href: '#hero',    icon: 'pi pi-home' },
  { label: 'Statistik', href: '#stats',   icon: 'pi pi-chart-bar' },
  { label: 'Peta',      href: '#map',     icon: 'pi pi-map' },
  { label: 'Program',   href: '#program', icon: 'pi pi-list' },
  // { label: 'Tentang', href: '#tentang', icon: 'pi pi-info-circle' }, // hidden sementara
]

async function handleLogout() {
  profileOpen.value = false
  mobileOpen.value  = false
  await authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.nav-link:hover { background: #f0fdf4; color: #15803d; }
.btn-login:hover { background: #15803d !important; }

@media (max-width: 768px) {
  .nav-desktop { display: none !important; }
  .nav-mobile  { display: flex !important; }
}
</style>
