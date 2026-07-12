import api from './api'

// Provinsi list (sesuai akses)
export async function fetchBaselineProvinsi() {
  const res = await api.get('/baseline/provinsi')
  return res.data?.data ?? []
}

// Dropdown wilayah: provinsi + kabkota + kecamatan sesuai skala LAZ
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

// Anggota list
export async function fetchBaselineAnggota(params = {}) {
  const res = await api.get('/baseline/anggota', { params })
  return res.data
}

// Anggota detail by NIK
export async function fetchBaselineAnggotaByNik(nik) {
  const res = await api.get('/baseline/anggota', { params: { provinsi: 'all', search: nik } })
  // Fallback: coba semua provinsi dengan search NIK
  const items = res.data?.data ?? []
  return items.find(r => r.nomor_induk_kependudukan === nik || r.nik === nik) ?? items[0] ?? null
}

// Keluarga list
export async function fetchBaselineKeluarga(params = {}) {
  const res = await api.get('/baseline/keluarga', { params })
  return res.data
}

// Keluarga detail by NKK
export async function fetchBaselineKeluargaByNkk(nkk) {
  const res = await api.get('/baseline/keluarga', { params: { search: nkk } })
  const items = res.data?.data ?? []
  return items.find(r => r.nomor_kartu_keluarga === nkk) ?? items[0] ?? null
}
