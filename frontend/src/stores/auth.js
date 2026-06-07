import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// ─── PROTOTYPE: no real API calls ────────────────────────────────────────────
// Dummy credentials: any username + any password will work for prototype
// OTP Email  : 845988
// OTP WA     : 990087
// ─────────────────────────────────────────────────────────────────────────────

const DUMMY_OTP_EMAIL = '845988'
const DUMMY_OTP_WA    = '990087'

export const useAuthStore = defineStore('auth', () => {
  // Hydrate from localStorage so page refresh doesn't reset mid-flow
  const user              = ref(JSON.parse(localStorage.getItem('dtsen_user') || 'null'))
  const accessToken       = ref(localStorage.getItem('dtsen_token') || null)
  const emailOtpVerified  = ref(localStorage.getItem('dtsen_otp_email') === 'true')
  const waOtpVerified     = ref(localStorage.getItem('dtsen_otp_wa')    === 'true')

  // Fully authenticated = logged in AND both OTPs verified
  const isAuthenticated   = computed(() => !!accessToken.value)
  const isOtpComplete     = computed(() => emailOtpVerified.value && waOtpVerified.value)
  const canAccessDashboard = computed(() => isAuthenticated.value && isOtpComplete.value)

  // ── login (dummy – accepts any credential) ───────────────────────────────
  function login(email, password) {
    if (!email || !password) throw new Error('Email dan password wajib diisi.')
    const dummyUser = { name: 'Admin DTSEN', email, role: 'admin' }
    const dummyToken = 'proto-token-' + Date.now()

    accessToken.value      = dummyToken
    user.value             = dummyUser
    emailOtpVerified.value = false
    waOtpVerified.value    = false

    localStorage.setItem('dtsen_token',     dummyToken)
    localStorage.setItem('dtsen_user',      JSON.stringify(dummyUser))
    localStorage.setItem('dtsen_otp_email', 'false')
    localStorage.setItem('dtsen_otp_wa',    'false')
  }

  // ── verify email OTP ──────────────────────────────────────────────────────
  function verifyEmailOtp(code) {
    if (code.trim() !== DUMMY_OTP_EMAIL) throw new Error('Kode OTP Email tidak valid.')
    emailOtpVerified.value = true
    localStorage.setItem('dtsen_otp_email', 'true')
  }

  // ── verify WA OTP ─────────────────────────────────────────────────────────
  function verifyWaOtp(code) {
    if (code.trim() !== DUMMY_OTP_WA) throw new Error('Kode OTP WhatsApp tidak valid.')
    waOtpVerified.value = true
    localStorage.setItem('dtsen_otp_wa', 'true')
  }

  // ── logout ────────────────────────────────────────────────────────────────
  function logout() {
    accessToken.value      = null
    user.value             = null
    emailOtpVerified.value = false
    waOtpVerified.value    = false
    ;['dtsen_token','dtsen_user','dtsen_otp_email','dtsen_otp_wa'].forEach(k => localStorage.removeItem(k))
  }

  return {
    user, accessToken,
    emailOtpVerified, waOtpVerified,
    isAuthenticated, isOtpComplete, canAccessDashboard,
    login, verifyEmailOtp, verifyWaOtp, logout
  }
})
