import apiClient from './apiClient'

/**
 * Ambil semua field aktif (is_active=1) beserta referensi kodenya.
 * @returns {Promise<Array>} list TampilanDtsen
 */
export async function fetchTampilanDtsen() {
  const res = await apiClient.get('/api/v1/tampilan-dtsen')
  return res.data?.data ?? []
}

/**
 * Ambil hanya field yang bisa dijadikan filter (is_filter=1 & is_active=1).
 * Digunakan untuk membangun panel filter dinamis di halaman Mustahik.
 * @returns {Promise<Array>} list filter fields
 */
export async function fetchFilterFields() {
  const res = await apiClient.get('/api/v1/tampilan-dtsen/filter')
  return res.data?.data ?? []
}
