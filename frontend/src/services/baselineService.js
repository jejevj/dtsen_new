import api from './api'

export async function fetchBaselineProvinsi() {
  const res = await api.get('/baseline/provinsi')
  return res.data?.data ?? []
}

/**
 * Tab Anggota — per provinsi, cursor-based
 * params: { provinsi, cursor?, search? }
 */
export async function fetchBaselineAnggota(params = {}) {
  const res = await api.get('/baseline/anggota', { params })
  return res.data
}

/**
 * Tab Keluarga — global, cursor-based
 * params: { cursor?, search? }
 */
export async function fetchBaselineKeluarga(params = {}) {
  const res = await api.get('/baseline/keluarga', { params })
  return res.data
}

// Alias lama agar komponen lain tidak breaking
export async function fetchBaselineData(params = {}) {
  return fetchBaselineAnggota(params)
}
