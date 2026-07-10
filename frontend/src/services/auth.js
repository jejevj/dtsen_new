import api from './api'

export const authService = {
  /**
   * Login — kirim identifier (email/notelp) + password ke backend
   */
  login(identifier, password) {
    return api.post('/auth/login', { identifier, password })
  },

  /**
   * Verifikasi token masih valid + ambil profil user saat ini
   */
  me() {
    return api.get('/auth/me')
  },

  /**
   * Logout — sinyal ke backend, hapus token di client
   */
  logout() {
    return api.post('/auth/logout').finally(() => {
      localStorage.removeItem('dtsen_access_token')
      localStorage.removeItem('dtsen_refresh_token')
      localStorage.removeItem('dtsen_user')
    })
  },

  /**
   * Refresh access token menggunakan refresh token
   */
  refresh() {
    const refreshToken = localStorage.getItem('dtsen_refresh_token')
    return api.post('/auth/refresh', {}, {
      headers: { Authorization: `Bearer ${refreshToken}` }
    })
  },
}
