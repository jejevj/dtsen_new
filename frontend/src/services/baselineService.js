import api from './api'

/**
 * Ambil daftar provinsi yang tersedia di Data Baseline.
 * @returns {Promise<Array<{kode:string, label:string}>>}
 */
export async function fetchBaselineProvinsi() {
  const res = await api.get('/baseline/provinsi')
  return res.data?.data ?? []
}

/**
 * Ambil data baseline ZAWA berdasarkan provinsi.
 * @param {object} params - { provinsi, page, per_page, search }
 * @returns {Promise<{data, columns, meta}>}
 */
export async function fetchBaselineData(params = {}) {
  const res = await api.get('/baseline', { params })
  return res.data
}
