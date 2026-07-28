import api from './api'

/**
 * Cek status maintenance dari backend.
 * @returns {Promise<{maintenance: boolean, message: string|null}>}
 */
export async function fetchMaintenanceStatus() {
  const res = await api.get('/options/maintenance')
  return res.data
}
