/**
 * m_tapilan_dtsen_ref
 * Referensi konversi kode → label untuk data DTSEN/ZAWA.
 */

export const JENIS_KELAMIN = {
  1: 'Laki-laki',
  2: 'Perempuan',
}

export const STATUS_KAWIN = {
  1: 'Belum Kawin',
  2: 'Kawin',
  3: 'Cerai Hidup',
  4: 'Cerai Mati',
}

export const HUBUNGAN_KELUARGA = {
  1: 'Kepala Keluarga',
  2: 'Istri / Suami',
  3: 'Anak',
  4: 'Menantu',
  5: 'Cucu',
  6: 'Orang Tua',
  7: 'Mertua',
  8: 'Famili Lain',
  9: 'Pembantu RT',
  10: 'Lainnya',
}

export const PENDIDIKAN = {
  0: 'Tidak / Belum Sekolah',
  1: 'Belum Tamat SD / Sederajat',
  2: 'Tamat SD / Sederajat',
  3: 'SLTP / Sederajat',
  4: 'SLTA / Sederajat',
  5: 'Diploma I / II',
  6: 'Akademi / Diploma III / Sarjana Muda',
  7: 'Diploma IV / Strata I',
  8: 'Strata II',
  9: 'Strata III',
}

export const STATUS_BEKERJA = {
  1: 'Bekerja',
  2: 'Tidak Bekerja',
  3: 'Belum / Tidak Bekerja',
}

export const DESIL_LABEL = {
  1: 'Desil 1 — Sangat Miskin',
  2: 'Desil 2 — Miskin',
  3: 'Desil 3 — Hampir Miskin',
  4: 'Desil 4 — Rentan Miskin',
}

export const DESIL_COLOR = {
  1: { bg: '#fef2f2', text: '#b91c1c', border: '#fca5a5' }, // red
  2: { bg: '#fff7ed', text: '#c2410c', border: '#fdba74' }, // orange
  3: { bg: '#fefce8', text: '#a16207', border: '#fde047' }, // yellow
  4: { bg: '#f0fdf4', text: '#15803d', border: '#86efac' }, // green
}

/** Helper: konversi kode → label, fallback ke nilai asli jika tidak dikenali */
export function resolveRef(map, value) {
  if (value == null || value === '') return '-'
  const key = Number(value)
  return map[key] ?? String(value)
}
