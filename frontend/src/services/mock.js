/**
 * Mock data service — digunakan saat backend belum tersedia.
 * Aktifkan dengan: VITE_USE_MOCK=true di .env
 */

export const mockHomeSummary = () => Promise.resolve({
  total_penyaluran: 8_340_000_000_000,
  penerima_manfaat: 3_218_450,
  nasional: 37,
  provinsi: 142,
  kabkota: 387
})

export const mockByGender = () => Promise.resolve({
  male_count:   1_874_210,
  female_count: 1_344_240,
  total:        3_218_450
})

export const mockByBidang = () => Promise.resolve([
  { bidang_label: 'Ekonomi',         total_penyaluran: 3_120_000_000_000 },
  { bidang_label: 'Pendidikan',      total_penyaluran: 1_860_000_000_000 },
  { bidang_label: 'Kesehatan',       total_penyaluran: 1_240_000_000_000 },
  { bidang_label: 'Kemanusiaan',     total_penyaluran:   980_000_000_000 },
  { bidang_label: 'Dakwah & Sosial', total_penyaluran:   740_000_000_000 },
  { bidang_label: 'Lingkungan',      total_penyaluran:   400_000_000_000 },
])

export const mockTimeseries = () => Promise.resolve([
  { tahun: '2019', Bantuan_Langsung: 1_100_000_000_000, Bantuan_Tidak_Langsung:   480_000_000_000 },
  { tahun: '2020', Bantuan_Langsung: 1_380_000_000_000, Bantuan_Tidak_Langsung:   620_000_000_000 },
  { tahun: '2021', Bantuan_Langsung: 1_650_000_000_000, Bantuan_Tidak_Langsung:   740_000_000_000 },
  { tahun: '2022', Bantuan_Langsung: 1_920_000_000_000, Bantuan_Tidak_Langsung:   890_000_000_000 },
  { tahun: '2023', Bantuan_Langsung: 2_310_000_000_000, Bantuan_Tidak_Langsung: 1_050_000_000_000 },
  { tahun: '2024', Bantuan_Langsung: 2_780_000_000_000, Bantuan_Tidak_Langsung: 1_220_000_000_000 },
])

export const mockMapData = () => Promise.resolve([
  { provinsi_kode: '31', provinsi_nama: 'DKI Jakarta',       mustahik: 420_300, penyaluran: 1_240_000_000_000, laz_count: 48 },
  { provinsi_kode: '32', provinsi_nama: 'Jawa Barat',        mustahik: 612_800, penyaluran: 1_580_000_000_000, laz_count: 72 },
  { provinsi_kode: '33', provinsi_nama: 'Jawa Tengah',       mustahik: 498_400, penyaluran:   980_000_000_000, laz_count: 61 },
  { provinsi_kode: '35', provinsi_nama: 'Jawa Timur',        mustahik: 534_700, penyaluran: 1_120_000_000_000, laz_count: 65 },
  { provinsi_kode: '34', provinsi_nama: 'DI Yogyakarta',     mustahik:  87_200, penyaluran:   210_000_000_000, laz_count: 19 },
  { provinsi_kode: '36', provinsi_nama: 'Banten',            mustahik: 198_500, penyaluran:   430_000_000_000, laz_count: 28 },
  { provinsi_kode: '11', provinsi_nama: 'Aceh',              mustahik: 142_600, penyaluran:   310_000_000_000, laz_count: 22 },
  { provinsi_kode: '12', provinsi_nama: 'Sumatera Utara',    mustahik: 187_400, penyaluran:   390_000_000_000, laz_count: 31 },
  { provinsi_kode: '13', provinsi_nama: 'Sumatera Barat',    mustahik:  98_300, penyaluran:   210_000_000_000, laz_count: 18 },
  { provinsi_kode: '14', provinsi_nama: 'Riau',              mustahik:  76_400, penyaluran:   168_000_000_000, laz_count: 14 },
  { provinsi_kode: '15', provinsi_nama: 'Jambi',             mustahik:  54_200, penyaluran:   112_000_000_000, laz_count: 11 },
  { provinsi_kode: '16', provinsi_nama: 'Sumatera Selatan',  mustahik:  93_700, penyaluran:   198_000_000_000, laz_count: 17 },
  { provinsi_kode: '17', provinsi_nama: 'Bengkulu',          mustahik:  32_100, penyaluran:    64_000_000_000, laz_count:  7 },
  { provinsi_kode: '18', provinsi_nama: 'Lampung',           mustahik:  88_600, penyaluran:   174_000_000_000, laz_count: 15 },
  { provinsi_kode: '19', provinsi_nama: 'Bangka Belitung',   mustahik:  21_400, penyaluran:    48_000_000_000, laz_count:  5 },
  { provinsi_kode: '21', provinsi_nama: 'Kepulauan Riau',    mustahik:  28_700, penyaluran:    62_000_000_000, laz_count:  7 },
  { provinsi_kode: '61', provinsi_nama: 'Kalimantan Barat',  mustahik:  67_300, penyaluran:   138_000_000_000, laz_count: 13 },
  { provinsi_kode: '62', provinsi_nama: 'Kalimantan Tengah', mustahik:  41_800, penyaluran:    86_000_000_000, laz_count:  9 },
  { provinsi_kode: '63', provinsi_nama: 'Kalimantan Selatan',mustahik:  58_200, penyaluran:   124_000_000_000, laz_count: 12 },
  { provinsi_kode: '64', provinsi_nama: 'Kalimantan Timur',  mustahik:  49_700, penyaluran:   108_000_000_000, laz_count: 10 },
  { provinsi_kode: '65', provinsi_nama: 'Kalimantan Utara',  mustahik:  14_300, penyaluran:    31_000_000_000, laz_count:  4 },
  { provinsi_kode: '71', provinsi_nama: 'Sulawesi Utara',    mustahik:  24_600, penyaluran:    52_000_000_000, laz_count:  7 },
  { provinsi_kode: '72', provinsi_nama: 'Sulawesi Tengah',   mustahik:  38_900, penyaluran:    78_000_000_000, laz_count:  9 },
  { provinsi_kode: '73', provinsi_nama: 'Sulawesi Selatan',  mustahik: 124_500, penyaluran:   264_000_000_000, laz_count: 21 },
  { provinsi_kode: '74', provinsi_nama: 'Sulawesi Tenggara', mustahik:  31_200, penyaluran:    66_000_000_000, laz_count:  8 },
  { provinsi_kode: '75', provinsi_nama: 'Gorontalo',         mustahik:  18_700, penyaluran:    38_000_000_000, laz_count:  5 },
  { provinsi_kode: '76', provinsi_nama: 'Sulawesi Barat',    mustahik:  16_400, penyaluran:    34_000_000_000, laz_count:  4 },
  { provinsi_kode: '51', provinsi_nama: 'Bali',              mustahik:  12_800, penyaluran:    28_000_000_000, laz_count:  5 },
  { provinsi_kode: '52', provinsi_nama: 'Nusa Tenggara Barat', mustahik: 94_200, penyaluran:  196_000_000_000, laz_count: 16 },
  { provinsi_kode: '53', provinsi_nama: 'Nusa Tenggara Timur', mustahik: 41_300, penyaluran:   84_000_000_000, laz_count:  9 },
  { provinsi_kode: '81', provinsi_nama: 'Maluku',            mustahik:  29_400, penyaluran:    58_000_000_000, laz_count:  7 },
  { provinsi_kode: '82', provinsi_nama: 'Maluku Utara',      mustahik:  19_800, penyaluran:    40_000_000_000, laz_count:  5 },
  { provinsi_kode: '91', provinsi_nama: 'Papua Barat',       mustahik:  14_100, penyaluran:    28_000_000_000, laz_count:  4 },
  { provinsi_kode: '94', provinsi_nama: 'Papua',             mustahik:  32_600, penyaluran:    64_000_000_000, laz_count:  8 },
])

export const mockSummary = () => Promise.resolve({
  penerima_manfaat: 3_218_450,
  penyaluran: 8_340_000_000_000
})

export const mockDesilSummary = () => Promise.resolve(
  Object.fromEntries(
    [0,1,2,3,4,5,6,7,8,9,10].map(i => [i, Math.round(Math.random() * 400_000 + 50_000)])
  )
)
