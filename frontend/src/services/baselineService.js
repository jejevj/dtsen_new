import api from './api'

// Provinsi list (sesuai akses)
// Response: [{ kode: "32", label: "Jawa Barat", slug: "jabar" }, ...]
export async function fetchBaselineProvinsi() {
  const res = await api.get('/baseline/provinsi')
  return res.data?.data ?? []
}

// Dropdown wilayah: provinsi + kabkota + kecamatan sesuai skala LAZ
export async function fetchWilayahDropdown(params = {}) {
  const res = await api.get('/wilayah/dropdown', { params })
  return res.data
}

/**
 * Kabkota by provinsi — gunakan kode BPS 2-digit ("32", "31", dst)
 * Endpoint /wilayah/kabkota menerima provinsi_kode = BPS kode
 */
export async function fetchKabkotaByBps(provinsi_kode) {
  if (!provinsi_kode) return []
  const res = await api.get('/wilayah/kabkota', { params: { provinsi_kode } })
  return res.data?.data ?? []
}

/**
 * @deprecated Gunakan fetchKabkotaByBps(bps_kode) — slug tidak diterima oleh /wilayah/kabkota
 */
export async function fetchKabkota(provinsi_kode) {
  return fetchKabkotaByBps(provinsi_kode)
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
