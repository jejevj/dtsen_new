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
export async function fetchBaselineAnggotaByNik(nik, wilayah = {}) {
  const nikStr = String(nik ?? '').trim()
  const params = { search: nikStr }
  for (const key of ['provinsi', 'kabkota_kode', 'kecamatan_kode']) {
    const value = wilayah[key]
    if (typeof value === 'string' && value.trim()) params[key] = value.trim()
  }
  if (params.provinsi) {
    const res = await api.get('/baseline/anggota', { params })
    return (res.data?.data ?? []).find(
      row => String(row.nomor_induk_kependudukan ?? row.nik ?? '').trim() === nikStr,
    ) ?? null
  }
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
        params: { ...params, provinsi: prov.kode },
      })
      const items = res.data?.data ?? []
      const found = items.find(
        r => String(r.nomor_induk_kependudukan ?? r.nik ?? '').trim() === nikStr,
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
import { decryptDtsen } from '@/utils/dtsenCrypto'


export async function fetchBaselineAnggotaDetailByHash(nikHash, wilayah = {}) {
  const value = String(nikHash ?? '').trim()
  const nik = /^\d{16}$/.test(value) ? value : decryptDtsen(value)
  if (!/^\d{16}$/.test(nik ?? '')) throw new Error('Token NIK tidak valid.')
  const data = await fetchBaselineAnggotaByNik(nik, wilayah)


  if (!data) return null


  return {

    ...data,


    nomor_induk_kependudukan:
      data.nomor_induk_kependudukan ?? decryptDtsen(
        data.nomor_induk_kependudukan_encrypt
      ),


    nomor_kartu_keluarga:
      data.nomor_kartu_keluarga ?? decryptDtsen(
        data.nomor_kartu_keluarga_encrypt
      ),


    tanggal_lahir:
      data.tanggal_lahir ?? decryptDtsen(
        data.tanggal_lahir_encrypt
      ),


    alamat_ktp:
      data.alamat_ktp ?? decryptDtsen(
        data.alamat_ktp_encrypt
      ),

  }
}
// Opsi data-baseline mengikuti penugasan t_dtsen_wilayah, termasuk kode null.
export async function fetchBaselineKabkota(provinsi_kode) {
  const res = await api.get('/baseline/kabkota', { params: { provinsi_kode } })
  return res.data?.data ?? []
}

export async function fetchBaselineKecamatan(kabkota_kode) {
  const res = await api.get('/baseline/kecamatan', { params: { kabkota_kode } })
  return res.data?.data ?? []
}
