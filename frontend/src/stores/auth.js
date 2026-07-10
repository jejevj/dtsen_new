import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  // ── State ─────────────────────────────────────────────────────────────────
  const user         = ref(JSON.parse(localStorage.getItem('dtsen_user') || 'null'))
  const accessToken  = ref(localStorage.getItem('dtsen_access_token') || null)
  const refreshToken = ref(localStorage.getItem('dtsen_refresh_token') || null)
  const loading      = ref(false)
  const error        = ref(null)

  // ── Computed ──────────────────────────────────────────────────────────────
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  // OTP dinonaktifkan sementara — langsung ke dashboard setelah login
  const isOtpComplete      = computed(() => true)
  const canAccessDashboard = computed(() => isAuthenticated.value)

  const isTuser = computed(() => user.value?.user_type === 'tuser')
  const isDtsen = computed(() => user.value?.user_type === 'dtsen')
  const userDisplayName = computed(() => {
    if (!user.value) return ''
    return user.value.user_fullname || user.value.nama_lengkap || user.value.email || ''
  })

  // ── Actions ───────────────────────────────────────────────────────────────

  /**
   * Login dengan email atau notelp + password.
   * Backend akan mencari di tuser dulu, lalu t_dtsen_akses.
   */
  async function login(identifier, password) {
    loading.value = true
    error.value   = null
    try {
      const { data } = await authService.login(identifier, password)

      accessToken.value  = data.access_token
      refreshToken.value = data.refresh_token
      user.value         = data.user

      localStorage.setItem('dtsen_access_token',  data.access_token)
      localStorage.setItem('dtsen_refresh_token', data.refresh_token)
      localStorage.setItem('dtsen_user',          JSON.stringify(data.user))

      return data
    } catch (err) {
      const msg = err.response?.data?.message || 'Login gagal. Periksa koneksi Anda.'
      error.value = msg
      throw new Error(msg)
    } finally {
      loading.value = false
    }
  }

  /**
   * Verifikasi token saat app dibuka / reload.
   * Jika 401, token dihapus otomatis oleh interceptor di api.js.
   */
  async function fetchMe() {
    if (!accessToken.value) return false
    try {
      const { data } = await authService.me()
      user.value = data
      localStorage.setItem('dtsen_user', JSON.stringify(data))
      return true
    } catch {
      return false
    }
  }

  /**
   * Logout — hapus semua state dan storage.
   */
  async function logout() {
    try {
      await authService.logout()
    } catch { /* abaikan error logout */ }
    finally {
      _clearState()
    }
  }

  function _clearState() {
    user.value         = null
    accessToken.value  = null
    refreshToken.value = null
    error.value        = null
    ;['dtsen_access_token', 'dtsen_refresh_token', 'dtsen_user'].forEach(k =>
      localStorage.removeItem(k)
    )
  }

  // Compat lama — masih dipakai beberapa komponen
  function verifyEmailOtp() {}
  function verifyWaOtp()    {}

  return {
    user, accessToken, refreshToken, loading, error,
    isAuthenticated, isOtpComplete, canAccessDashboard,
    isTuser, isDtsen, userDisplayName,
    login, logout, fetchMe,
    verifyEmailOtp, verifyWaOtp,
  }
})
