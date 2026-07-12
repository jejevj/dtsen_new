export const formatRupiah = (value) =>
  new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(value)

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
  if (abs >= 1_000)             return `${sign}${fmt(abs / 1_000)} Rb`
  return `${sign}${abs}`
}
