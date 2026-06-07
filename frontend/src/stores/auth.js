import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { findUserByEmail } from '@/data/mockUsers'

// ─── PROTOTYPE: no real API calls ────────────────────────────────────────────
// Password dummy untuk SEMUA user: dtsen2024
// OTP Email  : 845988
// OTP WA     : 990087
//
// Contoh akun:
//   admin@dtsen.go.id              → Admin Pusat (semua data)
//   analis.jabar@dtsen.go.id       → Analis Jawa Barat
//   op.kotabogor@dtsen.go.id       → Operator Kota Bogor
//   op.surabaya@dtsen.go.id        → Operator Kota Surabaya
//   (lihat frontend/src/data/mockUsers.js untuk daftar lengkap)
// ─────────────────────────────────────────────────────────────────────────────

const DUMMY_OTP_EMAIL  = '845988'
const DUMMY_OTP_WA     = '990087'
const DUMMY_PASSWORD   = 'dtsen2024'

export const useAuthStore = defineStore('auth', () => {
  const user             = ref(JSON.parse(localStorage.getItem('dtsen_user') || 'null'))
  const accessToken      = ref(localStorage.getItem('dtsen_token') || null)
  const emailOtpVerified = ref(localStorage.getItem('dtsen_otp_email') === 'true')
  const waOtpVerified    = ref(localStorage.getItem('dtsen_otp_wa')    === 'true')

  const isAuthenticated    = computed(() => !!accessToken.value)
  const isOtpComplete      = computed(() => emailOtpVerified.value && waOtpVerified.value)
  const canAccessDashboard = computed(() => isAuthenticated.value && isOtpComplete.value)

  // Wilayah aktif user yang sedang login
  const userWilayah = computed(() => user.value?.wilayah || null)

  // ── login ─────────────────────────────────────────────────────────────────
  function login(email, password) {
    if (!email || !password) throw new Error('Email dan password wajib diisi.')

    // Prototype: password harus dtsen2024 KECUALI ada email terdaftar di mockUsers
    const mockUser = findUserByEmail(email)

    if (mockUser) {
      // Email terdaftar → cek password dummy
      if (password !== DUMMY_PASSWORD) throw new Error('Password salah. Gunakan: dtsen2024')
    }
    // Email tidak terdaftar → gunakan fallback admin (backward-compat)
    const resolvedUser = mockUser || {
      name: 'Admin DTSEN',
      email,
      role: 'admin',
      wilayah: null,
      wilayah_label: 'Seluruh Indonesia',
    }

    const dummyToken = 'proto-token-' + Date.now()

    accessToken.value      = dummyToken
    user.value             = resolvedUser
    emailOtpVerified.value = false
    waOtpVerified.value    = false

    localStorage.setItem('dtsen_token',     dummyToken)
    localStorage.setItem('dtsen_user',      JSON.stringify(resolvedUser))
    localStorage.setItem('dtsen_otp_email', 'false')
    localStorage.setItem('dtsen_otp_wa',    'false')
  }

  // ── verify OTP ────────────────────────────────────────────────────────────
  function verifyEmailOtp(code) {
    if (code.trim() !== DUMMY_OTP_EMAIL) throw new Error('Kode OTP Email tidak valid.')
    emailOtpVerified.value = true
    localStorage.setItem('dtsen_otp_email', 'true')
  }

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
    user, accessToken, userWilayah,
    emailOtpVerified, waOtpVerified,
    isAuthenticated, isOtpComplete, canAccessDashboard,
    login, verifyEmailOtp, verifyWaOtp, logout,
  }
})
