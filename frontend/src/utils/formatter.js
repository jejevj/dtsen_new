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
