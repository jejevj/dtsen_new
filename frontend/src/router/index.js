import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },

  {
    path: '/verify-otp',
    name: 'verify-otp',
    component: () => import('@/views/OtpVerificationView.vue'),
    meta: { requiresLogin: true }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/mustahik',
    name: 'mustahik',
    component: () => import('@/views/MustahikView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/mustahik/:nikHashed',
    name: 'mustahik-detail',
    component: () => import('@/views/MustahikDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/cari-data',
    name: 'cari-data',
    component: () => import('@/views/CariDataView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/laporan',
    name: 'laporan',
    component: () => import('@/views/PemeriksaanDtsenView.vue'),
    meta: { requiresAuth: true }
  },
  { path: '/report', redirect: '/laporan' },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ── Navigation Guard ──────────────────────────────────────────────────────────
router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()

  // Halaman publik — langsung lanjut
  if (!to.meta.requiresAuth && !to.meta.requiresLogin) {
    // Jika sudah login dan mau ke /login → redirect dashboard
    if (to.name === 'login' && auth.isAuthenticated) return next({ name: 'dashboard' })
    return next()
  }

  // Belum ada token sama sekali
  if (!auth.accessToken) return next({ name: 'login' })

  // Ada token tapi user belum di-fetch (misal: reload browser)
  if (!auth.user) {
    const ok = await auth.fetchMe()
    if (!ok) return next({ name: 'login' })
  }

  // Semua OK
  next()
})

export default router
