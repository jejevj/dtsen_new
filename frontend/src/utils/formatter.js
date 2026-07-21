export const formatRupiah = (value) =>
  new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(value)

export const formatAngka = (value) =>
  new Intl.NumberFormat('id-ID', { style: 'decimal', minimumFractionDigits: 0 }).format(value)

export const formatDate = (value) => {
  if (!value) return '-'
  return new Intl.DateTimeFormat('id-ID', { day: '2-digit', month: 'long', year: 'numeric' }).format(new Date(value))
}

export const formatGender = (value) => {
  if (value === 'm') return 'Laki-laki'
  if (value === 'f') return 'Perempuan'
  return '-'
}

/**
 * Mengubah angka menjadi format singkat dengan satuan Rb / Jt / M / T
 * Contoh:
 *   690000        → "690 Rb"
 *   1560000       → "1,5 Jt"
 *   250000000     → "250 Jt"
 *   1500000000    → "1,5 M"
 *   3200000000000 → "3,2 T"
 *
 * @param {number} value
 * @param {number} [decimals=1] - jumlah desimal (default 1)
 * @returns {string}
 */
export const formatShort = (value, decimals = 1) => {
  if (value === null || value === undefined || isNaN(value)) return '-'

  const abs = Math.abs(value)
  const sign = value < 0 ? '-' : ''

  const fmt = (num) =>
    parseFloat(num.toFixed(decimals))
      .toLocaleString('id-ID', { maximumFractionDigits: decimals })

  if (abs >= 1_000_000_000_000) return `${sign}${fmt(abs / 1_000_000_000_000)} T`
  if (abs >= 1_000_000_000)     return `${sign}${fmt(abs / 1_000_000_000)} M`
  if (abs >= 1_000_000)         return `${sign}${fmt(abs / 1_000_000)} Jt`
  if (abs >= 10_000)             return `${sign}${fmt(abs / 1_000)} Rb`
  if (abs >= 1_000)             return `${sign}${fmt(abs)}`
  return `${sign}${abs}`
}

export const formatShortM = (value, decimals = 1) => {
  if (value === null || value === undefined || isNaN(value)) return '-'

  const abs = Math.abs(value)
  const sign = value < 0 ? '-' : ''

  const fmt = (num) =>
    parseFloat(num.toFixed(decimals))
      .toLocaleString('id-ID', { maximumFractionDigits: decimals })

  if (abs >= 1_000_000_000_000) return `${sign}${fmt(abs / 1_000_000_000_000)} T`
  if (abs >= 1_000_000_000)     return `${sign}${fmt(abs / 1_000_000_000)} M`
  if (abs >= 1_000_000)         return `${sign}${fmt(abs / 1_000_000)} Jt`
  else return `${sign}${fmt(abs)}`
  return `${sign}${abs}`
}

/**
 * Masking NIK: tampilkan 4 digit awal + bintang tengah + 4 digit akhir.
 * Contoh: 3578116503040003 → 3578********0003
 *
 * @param {string|number|null} nik
 * @param {number} [visibleStart=4] - digit yang terlihat di awal
 * @param {number} [visibleEnd=4]   - digit yang terlihat di akhir
 * @returns {string}
 */
export function maskNik(nik, visibleStart = 4, visibleEnd = 4) {
  if (!nik && nik !== 0) return '-'
  const str = String(nik).trim()
  if (str === '-' || str === '') return '-'
  const total = str.length
  if (total <= visibleStart + visibleEnd) return str   // terlalu pendek, tampilkan utuh
  const start  = str.slice(0, visibleStart)
  const end    = str.slice(total - visibleEnd)
  const masked = '*'.repeat(total - visibleStart - visibleEnd)
  return `${start}${masked}${end}`
}
