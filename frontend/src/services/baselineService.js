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

/**
 * Anggota detail by NIK — iterasi per-provinsi sampai ditemukan.
 * Backend TIDAK mendukung provinsi:'all', jadi harus loop.
 * NIK mengandung kode provinsi pada 2 digit pertama sehingga kita
 * coba provinsi yang sesuai lebih dulu agar cepat.
 */
export async function fetchBaselineAnggotaByNik(nik) {
  const nikStr = String(nik ?? '').trim()
  const provinsiList = await fetchBaselineProvinsi()

  // Urutkan: provinsi yang kode BPS-nya cocok dengan 2 digit awal NIK didahulukan
  const nikProv = nikStr.slice(0, 2)
  const sorted = [
    ...provinsiList.filter(p => String(p.kode ?? '').padStart(2, '0') === nikProv.padStart(2, '0')),
    ...provinsiList.filter(p => String(p.kode ?? '').padStart(2, '0') !== nikProv.padStart(2, '0')),
  ]

  for (const prov of sorted) {
    try {
      const res = await api.get('/baseline/anggota', {
        params: { provinsi: prov.kode, search: nikStr },
      })
      const items = res.data?.data ?? []
      const found = items.find(
        r => r.nomor_induk_kependudukan === nikStr || r.nik === nikStr,
      )
      if (found) return found
    } catch {
      // lanjut ke provinsi berikutnya bila timeout / error
    }
  }
  return null
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

// Anggota detail by encrypted NIK
export async function fetchBaselineAnggotaDetailByHash(nikHash) {

  if (!nikHash) return null

  const res = await api.get(
    `/baseline/anggota/detail/${encodeURIComponent(nikHash)}`
  )

  return res.data?.data ?? null
}