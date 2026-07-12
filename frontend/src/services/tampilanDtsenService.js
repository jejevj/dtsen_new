import api from './api'

/**
 * Ambil semua field aktif (is_active=1) beserta referensi kodenya.
 * baseURL di api.js sudah /api/v1, jadi cukup path relatifnya.
 * @returns {Promise<Array>}
 */
export async function fetchTampilanDtsen() {
  const res = await api.get('/tampilan-dtsen')
  return res.data?.data ?? []
}

/**
 * Ambil hanya field yang bisa dijadikan filter (is_filter=1 & is_active=1).
 * Digunakan untuk membangun panel filter dinamis di halaman Mustahik.
 * @returns {Promise<Array>}
 */
export async function fetchFilterFields() {
  const res = await api.get('/tampilan-dtsen/filter')
  return res.data?.data ?? []
}
