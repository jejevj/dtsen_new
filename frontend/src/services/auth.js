import api from './api'

export const authService = {
  /** Step 1 — Login: kirim credentials, server kirim OTP ke email. */
  login(identifier, password) {
    return api.post('/auth/login', { identifier, password })
  },

  /** Step 2 — Verifikasi OTP Email → server kirim OTP ke WA. */
  verifyEmailOtp(otp_key, code) {
    return api.post('/auth/otp/verify-email', { otp_key, code })
  },

  /** Step 3 — Verifikasi OTP WA → terima JWT. */
  verifyWaOtp(wa_otp_key, code) {
    return api.post('/auth/otp/verify-wa', { wa_otp_key, code })
  },

  resendEmailOtp(otp_key)     { return api.post('/auth/otp/resend-email', { otp_key }) },
  resendWaOtp(wa_otp_key)     { return api.post('/auth/otp/resend-wa',    { wa_otp_key }) },

  me()     { return api.get('/auth/me') },
  logout() { return api.post('/auth/logout') },
}
