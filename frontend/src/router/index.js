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
    meta: { requiresAuth: true, requiresOtp: true }
  },
  {
    path: '/mustahik',
    name: 'mustahik',
    component: () => import('@/views/MustahikView.vue'),
    meta: { requiresAuth: true, requiresOtp: true }
  },
  {
    path: '/mustahik/:nikHashed',
    name: 'mustahik-detail',
    component: () => import('@/views/MustahikDetailView.vue'),
    meta: { requiresAuth: true, requiresOtp: true }
  },
  {
    path: '/report',
    name: 'report',
    component: () => import('@/views/ReportView.vue'),
    meta: { requiresAuth: true, requiresOtp: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()

  // Route requires full OTP verification
  if (to.meta.requiresOtp) {
    if (!auth.isAuthenticated) return next({ name: 'login' })
    if (!auth.isOtpComplete)   return next({ name: 'verify-otp' })
    return next()
  }

  // Route requires login only (OTP page itself)
  if (to.meta.requiresLogin) {
    if (!auth.isAuthenticated) return next({ name: 'login' })
    // Already completed OTP → skip OTP page, go to dashboard
    if (auth.isOtpComplete)    return next({ name: 'dashboard' })
    return next()
  }

  // Old requiresAuth guard (fallback compat)
  if (to.meta.requiresAuth && !auth.canAccessDashboard) {
    return next({ name: 'login' })
  }

  next()
})

export default router
