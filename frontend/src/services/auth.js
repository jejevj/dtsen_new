import api from './api'

export const authService = {
  /**
   * Step 1 — Login: kirim credentials, server kirim OTP ke email.
   * Response: { message, otp_key, otp_sent, user_hint }
   */
  login(identifier, password) {
    return api.post('/auth/login', { identifier, password })
  },

  /**
   * Step 2 — Verify OTP: kirim kode + otp_key, terima JWT.
   * Response: { access_token, refresh_token, user }
   */
  verifyOtp(otp_key, code) {
    return api.post('/auth/otp/verify', { otp_key, code })
  },

  /**
   * Kirim ulang OTP.
   */
  resendOtp(otp_key) {
    return api.post('/auth/otp/resend', { otp_key })
  },

  me()     { return api.get('/auth/me') },
  logout() { return api.post('/auth/logout') },
}
