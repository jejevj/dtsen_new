import axios from 'axios'
import router from '@/router'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// ── Request: attach access token ───────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('dtsen_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Response: auto-refresh hanya pada 401, queue concurrent requests ──────
let isRefreshing = false
let failedQueue  = []

function processQueue(error, token = null) {
  failedQueue.forEach(p => error ? p.reject(error) : p.resolve(token))
  failedQueue = []
}

async function getAuthStore() {
  try {
    const { useAuthStore } = await import('@/stores/auth')
    return useAuthStore()
  } catch {
    return null
  }
}

api.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config

    // Hanya tangani 401, biarkan status lain (termasuk 422) lewat
    if (err.response?.status !== 401 || original._retry) {
      return Promise.reject(err)
    }

    original._retry = true

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

    if (!refreshToken) {
      isRefreshing = false
      await _forceLogout()
      return Promise.reject(err)
    }

    try {
      const { data } = await axios.post(
        BASE_URL + '/auth/refresh',
        {},
        { headers: { Authorization: `Bearer ${refreshToken}` } }
      )

      const newToken = data.access_token
      localStorage.setItem('dtsen_access_token', newToken)

      const authStore = await getAuthStore()
      if (authStore) authStore.accessToken = newToken

      processQueue(null, newToken)

      original.headers.Authorization = `Bearer ${newToken}`
      return api(original)

    } catch (refreshErr) {
      processQueue(refreshErr, null)
      await _forceLogout()
      return Promise.reject(refreshErr)
    } finally {
      isRefreshing = false
    }
  }
)

async function _forceLogout() {
  const authStore = await getAuthStore()
  if (authStore && typeof authStore._clearState === 'function') {
    authStore._clearState()
  } else {
    ;['dtsen_access_token', 'dtsen_refresh_token', 'dtsen_user'].forEach(k =>
      localStorage.removeItem(k)
    )
  }
  router.push({ name: 'login' })
}

export default api
