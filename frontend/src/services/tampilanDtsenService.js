import api from './api'

/**
 * Ambil semua field aktif (is_active=1) beserta referensi kodenya.
 * @returns {Promise<Array>}
 */
export async function fetchTampilanDtsen() {
  const res = await api.get('/tampilan-dtsen')
  return res.data?.data ?? []
}

/**
 * Ambil hanya field yang bisa dijadikan filter (is_filter=1 & is_active=1).
 * @param {string|null} kategori - 'individu' | 'keluarga' | null (semua)
 * @returns {Promise<Array>}
 */
export async function fetchFilterFields(kategori = null) {
  const params = kategori ? { kategori } : {}
  const res = await api.get('/tampilan-dtsen/filter', { params })
  return res.data?.data ?? []
}
