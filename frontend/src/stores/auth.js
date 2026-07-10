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

  // Disimpan sementara selama proses OTP (tidak di-persist)
  const pendingOtpKey   = ref(sessionStorage.getItem('dtsen_otp_key') || null)
  const pendingUserHint = ref(JSON.parse(sessionStorage.getItem('dtsen_otp_hint') || 'null'))

  // ── Computed ──────────────────────────────────────────────────────────────
  const isAuthenticated    = computed(() => !!accessToken.value && !!user.value)
  const hasPendingOtp      = computed(() => !!pendingOtpKey.value)
  const canAccessDashboard = computed(() => isAuthenticated.value)

  const isTuser = computed(() => user.value?.user_type === 'tuser')
  const isDtsen = computed(() => user.value?.user_type === 'dtsen')
  const userDisplayName = computed(() => {
    if (!user.value) return ''
    return user.value.user_fullname || user.value.nama_lengkap || user.value.email || ''
  })

  // ── Actions ───────────────────────────────────────────────────────────────

  /**
   * Step 1 — Login: kirim credentials ke backend.
   * Backend kirim OTP ke email, frontend redirect ke /verify-otp.
   */
  async function login(identifier, password) {
    loading.value = true
    error.value   = null
    try {
      const { data } = await authService.login(identifier, password)
      // Simpan otp_key & hint di sessionStorage (hilang saat tab ditutup)
      pendingOtpKey.value   = data.otp_key
      pendingUserHint.value = data.user_hint
      sessionStorage.setItem('dtsen_otp_key',  data.otp_key)
      sessionStorage.setItem('dtsen_otp_hint', JSON.stringify(data.user_hint))
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
   * Step 2 — Verifikasi OTP email: kirim kode ke backend.
   * Jika benar, terima JWT dan simpan.
   */
  async function verifyEmailOtp(code) {
    loading.value = true
    error.value   = null
    try {
      const { data } = await authService.verifyOtp(pendingOtpKey.value, code)
      accessToken.value  = data.access_token
      refreshToken.value = data.refresh_token
      user.value         = data.user
      localStorage.setItem('dtsen_access_token',  data.access_token)
      localStorage.setItem('dtsen_refresh_token', data.refresh_token)
      localStorage.setItem('dtsen_user',          JSON.stringify(data.user))
      _clearOtpPending()
      return data
    } catch (err) {
      const msg = err.response?.data?.message || 'Kode OTP salah atau sudah kadaluarsa.'
      error.value = msg
      throw new Error(msg)
    } finally {
      loading.value = false
    }
  }

  async function resendOtp() {
    return authService.resendOtp(pendingOtpKey.value)
  }

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

  async function logout() {
    try { await authService.logout() } catch { /* abaikan */ }
    finally { _clearState() }
  }

  function _clearOtpPending() {
    pendingOtpKey.value   = null
    pendingUserHint.value = null
    sessionStorage.removeItem('dtsen_otp_key')
    sessionStorage.removeItem('dtsen_otp_hint')
  }

  function _clearState() {
    user.value = null; accessToken.value = null; refreshToken.value = null; error.value = null
    _clearOtpPending()
    ;['dtsen_access_token','dtsen_refresh_token','dtsen_user'].forEach(k => localStorage.removeItem(k))
  }

  return {
    user, accessToken, refreshToken, loading, error,
    pendingOtpKey, pendingUserHint,
    isAuthenticated, hasPendingOtp, canAccessDashboard,
    isTuser, isDtsen, userDisplayName,
    login, logout, fetchMe, verifyEmailOtp, resendOtp,
  }
})
