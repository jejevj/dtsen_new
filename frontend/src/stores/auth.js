import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  const user         = ref(JSON.parse(localStorage.getItem('dtsen_user') || 'null'))
  const accessToken  = ref(localStorage.getItem('dtsen_access_token') || null)
  const refreshToken = ref(localStorage.getItem('dtsen_refresh_token') || null)
  const loading      = ref(false)
  const error        = ref(null)

  // OTP step 1 — Email
  const pendingOtpKey   = ref(sessionStorage.getItem('dtsen_otp_key')   || null)
  const pendingUserHint = ref(JSON.parse(sessionStorage.getItem('dtsen_otp_hint') || 'null'))

  // OTP step 2 — WA
  const pendingWaKey    = ref(sessionStorage.getItem('dtsen_wa_key')    || null)
  const pendingWaHint   = ref(JSON.parse(sessionStorage.getItem('dtsen_wa_hint')  || 'null'))

  // Nomor HP user — disimpan saat login berhasil (sudah 628xxx)
  const pendingPhone    = ref(sessionStorage.getItem('dtsen_pending_phone') || null)

  const isAuthenticated    = computed(() => !!accessToken.value && !!user.value)
  const hasPendingOtp      = computed(() => !!pendingOtpKey.value)
  const hasPendingWaOtp    = computed(() => !!pendingWaKey.value)
  const canAccessDashboard = computed(() => isAuthenticated.value)

  const isTuser = computed(() => user.value?.user_type === 'tuser')
  const isDtsen = computed(() => user.value?.user_type === 'dtsen')
  const userDisplayName = computed(() => {
    if (!user.value) return ''
    return user.value.user_fullname || user.value.nama_lengkap || user.value.email || ''
  })

  /** Login → OTP email dikirim, simpan otp_key + phone */
  async function login(identifier, password) {
    loading.value = true; error.value = null
    try {
      const { data } = await authService.login(identifier, password)
      pendingOtpKey.value   = data.otp_key
      pendingUserHint.value = data.user_hint
      const phone = data.user_hint?.phone || ''
      pendingPhone.value = phone
      sessionStorage.setItem('dtsen_otp_key',       data.otp_key)
      sessionStorage.setItem('dtsen_otp_hint',      JSON.stringify(data.user_hint))
      sessionStorage.setItem('dtsen_pending_phone', phone)
      return data
    } catch (err) {
      const msg = err.response?.data?.message || 'Login gagal.'
      error.value = msg; throw new Error(msg)
    } finally { loading.value = false }
  }

  /** Verifikasi OTP email → WA OTP dikirim, simpan wa_key */
  async function verifyEmailOtp(code) {
    loading.value = true; error.value = null
    try {
      const { data } = await authService.verifyEmailOtp(pendingOtpKey.value, code)
      pendingWaKey.value  = data.wa_otp_key
      pendingWaHint.value = data.user_hint
      sessionStorage.setItem('dtsen_wa_key',  data.wa_otp_key)
      sessionStorage.setItem('dtsen_wa_hint', JSON.stringify(data.user_hint))
      pendingOtpKey.value = null; pendingUserHint.value = null
      sessionStorage.removeItem('dtsen_otp_key')
      sessionStorage.removeItem('dtsen_otp_hint')
      return data
    } catch (err) {
      const msg = err.response?.data?.message || 'Kode OTP email salah.'
      error.value = msg; throw new Error(msg)
    } finally { loading.value = false }
  }

  /** Verifikasi OTP WA → terima JWT, simpan token */
  async function verifyWaOtp(code) {
    loading.value = true; error.value = null
    try {
      const { data } = await authService.verifyWaOtp(pendingWaKey.value, code)
      accessToken.value  = data.access_token
      refreshToken.value = data.refresh_token
      user.value         = data.user
      localStorage.setItem('dtsen_access_token',  data.access_token)
      localStorage.setItem('dtsen_refresh_token', data.refresh_token)
      localStorage.setItem('dtsen_user',          JSON.stringify(data.user))
      _clearOtpPending()
      return data
    } catch (err) {
      const msg = err.response?.data?.message || 'Kode OTP WhatsApp salah.'
      error.value = msg; throw new Error(msg)
    } finally { loading.value = false }
  }

  async function resendEmailOtp() {
    return authService.resendEmailOtp(pendingOtpKey.value)
  }
  async function resendWaOtp() {
    return authService.resendWaOtp(pendingWaKey.value)
  }

  async function fetchMe() {
    if (!accessToken.value) return false
    try {
      const { data } = await authService.me()
      user.value = data
      localStorage.setItem('dtsen_user', JSON.stringify(data))
      return true
    } catch { return false }
  }

  async function logout() {
    try { await authService.logout() } catch { }
    finally { clearState() }
  }

  function _clearOtpPending() {
    pendingOtpKey.value = null; pendingUserHint.value = null
    pendingWaKey.value  = null; pendingWaHint.value  = null
    pendingPhone.value  = null
    ;['dtsen_otp_key','dtsen_otp_hint','dtsen_wa_key','dtsen_wa_hint','dtsen_pending_phone']
      .forEach(k => sessionStorage.removeItem(k))
  }

  /**
   * Reset semua state auth + hapus localStorage.
   * Di-expose secara publik agar bisa dipanggil dari api.js (forceLogout)
   * tanpa circular dependency.
   */
  function clearState() {
    user.value = null; accessToken.value = null
    refreshToken.value = null; error.value = null
    _clearOtpPending()
    ;['dtsen_access_token','dtsen_refresh_token','dtsen_user']
      .forEach(k => localStorage.removeItem(k))
  }

  // Alias internal agar kode lama yang pakai _clearState masih jalan
  const _clearState = clearState

  return {
    user, accessToken, refreshToken, loading, error,
    pendingOtpKey, pendingUserHint, pendingWaKey, pendingWaHint, pendingPhone,
    isAuthenticated, hasPendingOtp, hasPendingWaOtp, canAccessDashboard,
    isTuser, isDtsen, userDisplayName,
    login, logout, fetchMe,
    verifyEmailOtp, verifyWaOtp, resendEmailOtp, resendWaOtp,
    clearState, _clearState,
  }
})
