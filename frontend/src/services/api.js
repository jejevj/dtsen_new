import axios from 'axios'
import router from '@/router'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// ── Request: attach access token ─────────────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('dtsen_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Response: handle 401 → auto-refresh, queue concurrent requests ────────────
let isRefreshing = false
let failedQueue  = []

function processQueue(error, token = null) {
  failedQueue.forEach(p => error ? p.reject(error) : p.resolve(token))
  failedQueue = []
}

/**
 * Lazy-load auth store untuk menghindari circular dependency saat module init.
 * Pinia store hanya tersedia setelah app Vue dibuat.
 */
function getAuthStore() {
  try {
    // Dynamic import-like: ambil store hanya saat dibutuhkan
    const { useAuthStore } = require('@/stores/auth')
    return useAuthStore()
  } catch {
    return null
  }
}

api.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config

    // Hanya tangani 401, dan jangan retry kalau sudah pernah retry
    if (err.response?.status !== 401 || original._retry) {
      return Promise.reject(err)
    }

    original._retry = true

    // Jika sudah ada proses refresh berjalan, antri request ini
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      }).then(token => {
        original.headers.Authorization = `Bearer ${token}`
        return api(original)
      }).catch(e => Promise.reject(e))
    }

    isRefreshing = true
    const refreshToken = localStorage.getItem('dtsen_refresh_token')

    // Tidak ada refresh token → langsung logout
    if (!refreshToken) {
      isRefreshing = false
      _forceLogout()
      return Promise.reject(err)
    }

    try {
      const { data } = await axios.post(
        BASE_URL + '/auth/refresh',
        {},
        { headers: { Authorization: `Bearer ${refreshToken}` } }
      )

      const newToken = data.access_token

      // 1. Update localStorage
      localStorage.setItem('dtsen_access_token', newToken)

      // 2. Sync Pinia store agar state Vue tidak stale
      const authStore = getAuthStore()
      if (authStore) {
        authStore.accessToken = newToken
      }

      // 3. Selesaikan semua request yang sedang antri
      processQueue(null, newToken)

      // 4. Retry request original dengan token baru
      original.headers.Authorization = `Bearer ${newToken}`
      return api(original)

    } catch (refreshErr) {
      processQueue(refreshErr, null)
      _forceLogout()
      return Promise.reject(refreshErr)
    } finally {
      isRefreshing = false
    }
  }
)

/**
 * Clear semua auth state dan redirect ke halaman login.
 * Prioritas: gunakan Pinia store._clearState() jika tersedia,
 * fallback ke manual localStorage clear.
 */
function _forceLogout() {
  const authStore = getAuthStore()
  if (authStore && typeof authStore._clearState === 'function') {
    authStore._clearState()
  } else {
    // Fallback manual jika store belum tersedia
    ;['dtsen_access_token', 'dtsen_refresh_token', 'dtsen_user'].forEach(k =>
      localStorage.removeItem(k)
    )
  }
  router.push({ name: 'login' })
}

export default api
