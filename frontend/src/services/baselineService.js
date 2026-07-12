import api from './api'

// Provinsi list (sesuai akses)
export async function fetchBaselineProvinsi() {
  const res = await api.get('/baseline/provinsi')
  return res.data?.data ?? []
}

// Dropdown wilayah: provinsi + kabkota + kecamatan sesuai skala LAZ
// params: { provinsi_kode?, kabkota_kode? }
export async function fetchWilayahDropdown(params = {}) {
  const res = await api.get('/wilayah/dropdown', { params })
  return res.data
}

// Kabkota by provinsi
export async function fetchKabkota(provinsi_kode) {
  const res = await api.get('/wilayah/kabkota', { params: { provinsi_kode } })
  return res.data?.data ?? []
}

// Kecamatan by kabkota
export async function fetchKecamatan(kabkota_kode) {
  const res = await api.get('/wilayah/kecamatan', { params: { kabkota_kode } })
  return res.data?.data ?? []
}

// Anggota
export async function fetchBaselineAnggota(params = {}) {
  const res = await api.get('/baseline/anggota', { params })
  return res.data
}

// Keluarga
export async function fetchBaselineKeluarga(params = {}) {
  const res = await api.get('/baseline/keluarga', { params })
  return res.data
}
