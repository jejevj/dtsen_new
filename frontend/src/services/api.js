import axios from 'axios'
import router from '@/router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// ── Request: attach access token ─────────────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('dtsen_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Response: handle 401 → coba refresh dulu, baru redirect login ─────────────
let isRefreshing = false
let failedQueue  = []

function processQueue(error, token = null) {
  failedQueue.forEach(p => error ? p.reject(error) : p.resolve(token))
  failedQueue = []
}

api.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config

    if (err.response?.status === 401 && !original._retry) {
      original._retry = true

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          original.headers.Authorization = `Bearer ${token}`
          return api(original)
        })
      }

      isRefreshing = true
      const refreshToken = localStorage.getItem('dtsen_refresh_token')

      if (!refreshToken) {
        isRefreshing = false
        router.push({ name: 'login' })
        return Promise.reject(err)
      }

      try {
        const { data } = await axios.post(
          (import.meta.env.VITE_API_BASE_URL || '/api/v1') + '/auth/refresh',
          {},
          { headers: { Authorization: `Bearer ${refreshToken}` } }
        )
        const newToken = data.access_token
        localStorage.setItem('dtsen_access_token', newToken)
        processQueue(null, newToken)
        original.headers.Authorization = `Bearer ${newToken}`
        return api(original)
      } catch (refreshErr) {
        processQueue(refreshErr, null)
        localStorage.removeItem('dtsen_access_token')
        localStorage.removeItem('dtsen_refresh_token')
        localStorage.removeItem('dtsen_user')
        router.push({ name: 'login' })
        return Promise.reject(refreshErr)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(err)
  }
)

export default api
