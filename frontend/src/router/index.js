import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore }       from '@/stores/auth'
import { useLoginModalStore } from '@/stores/loginModal'

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },

  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue')
  },

  {
    path: '/verify-otp',
    name: 'verify-otp',
    component: () => import('@/views/OtpVerificationView.vue'),
    meta: { requiresOtp: true }
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
    path: '/data-baseline',
    name: 'data-baseline',
    component: () => import('@/views/DataBaselineView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/data-baseline/anggota/:nik',
    name: 'baseline-anggota-detail',
    component: () => import('@/views/AnggotaDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/data-baseline/keluarga/:nkk',
    name: 'baseline-keluarga-detail',
    component: () => import('@/views/KeluargaDetailView.vue'),
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

router.beforeEach(async (to, _from, next) => {
  const auth       = useAuthStore()
  const loginModal = useLoginModalStore()

  if (to.meta.requiresOtp) {
    if (!auth.pendingOtpKey) {
      return next({ name: 'home' })
    }
    return next()
  }

  if (!to.meta.requiresAuth) return next()

  if (!auth.accessToken) {
    loginModal.open()
    return next({ name: 'home' })
  }

  if (!auth.user) {
    const ok = await auth.fetchMe()
    if (!ok) {
      loginModal.open()
      return next({ name: 'home' })
    }
  }

  next()
})

export default router
