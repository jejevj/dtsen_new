import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

/**
 * Custom JSON parser yang mempertahankan presisi angka panjang (NKK/NIK 16 digit+).
 * Angka >= 16 digit di-wrap jadi string sebelum JSON.parse() agar tidak
 * kehilangan digit akibat IEEE 754 floating point precision.
 */
function parseSafeJSON(text) {
  // Ganti semua angka >= 16 digit yang belum dibungkus tanda kutip menjadi string
  const safe = text.replace(/(:\s*)(\d{16,})([,\}\]])/g, '$1"$2"$3')
  return JSON.parse(safe)
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
  transformResponse: [
    (data) => {
      if (typeof data === 'string') {
        try {
          return parseSafeJSON(data)
        } catch {
          return data
        }
      }
      return data
    },
  ],
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const auth = useAuthStore()
      auth.clearState()
    }
    return Promise.reject(error)
  }
)

export default api
