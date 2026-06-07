// ─── DUMMY USERS PER WILAYAH ────────────────────────────────────────────────
// Semua password dummy: "dtsen2024"
// Setiap user hanya melihat data mustahik di wilayah (provinsi/kab_kota/kecamatan) miliknya
// Role:
//   admin    → akses semua wilayah (wilayah: null = no filter)
//   operator → akses per kab_kota
//   analis   → akses per provinsi

export const DUMMY_USERS = [
  // ── SUPER ADMIN (akses semua data) ─────────────────────────────────────────
  {
    email: 'admin@dtsen.go.id',
    name: 'Admin Pusat DTSEN',
    role: 'admin',
    wilayah: null, // null = tampilkan semua data
    wilayah_label: 'Seluruh Indonesia',
  },

  // ── ANALIS PROVINSI ─────────────────────────────────────────────────────────
  {
    email: 'analis.jabar@dtsen.go.id',
    name: 'Analis Jawa Barat',
    role: 'analis',
    wilayah: { level: 'provinsi', value: 'Jawa Barat' },
    wilayah_label: 'Provinsi Jawa Barat',
  },
  {
    email: 'analis.banten@dtsen.go.id',
    name: 'Analis Banten',
    role: 'analis',
    wilayah: { level: 'provinsi', value: 'Banten' },
    wilayah_label: 'Provinsi Banten',
  },
  {
    email: 'analis.jateng@dtsen.go.id',
    name: 'Analis Jawa Tengah',
    role: 'analis',
    wilayah: { level: 'provinsi', value: 'Jawa Tengah' },
    wilayah_label: 'Provinsi Jawa Tengah',
  },
  {
    email: 'analis.jatim@dtsen.go.id',
    name: 'Analis Jawa Timur',
    role: 'analis',
    wilayah: { level: 'provinsi', value: 'Jawa Timur' },
    wilayah_label: 'Provinsi Jawa Timur',
  },
  {
    email: 'analis.dki@dtsen.go.id',
    name: 'Analis DKI Jakarta',
    role: 'analis',
    wilayah: { level: 'provinsi', value: 'DKI Jakarta' },
    wilayah_label: 'Provinsi DKI Jakarta',
  },
  {
    email: 'analis.yogya@dtsen.go.id',
    name: 'Analis D.I. Yogyakarta',
    role: 'analis',
    wilayah: { level: 'provinsi', value: 'D.I. Yogyakarta' },
    wilayah_label: 'Provinsi D.I. Yogyakarta',
  },
  {
    email: 'analis.sumut@dtsen.go.id',
    name: 'Analis Sumatera Utara',
    role: 'analis',
    wilayah: { level: 'provinsi', value: 'Sumatera Utara' },
    wilayah_label: 'Provinsi Sumatera Utara',
  },
  {
    email: 'analis.sulsel@dtsen.go.id',
    name: 'Analis Sulawesi Selatan',
    role: 'analis',
    wilayah: { level: 'provinsi', value: 'Sulawesi Selatan' },
    wilayah_label: 'Provinsi Sulawesi Selatan',
  },

  // ── OPERATOR KOTA/KAB ────────────────────────────────────────────────────────
  {
    email: 'op.kotabogor@dtsen.go.id',
    name: 'Operator Kota Bogor',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Kota Bogor' },
    wilayah_label: 'Kota Bogor',
  },
  {
    email: 'op.kabbogor@dtsen.go.id',
    name: 'Operator Kab. Bogor',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Kab. Bogor' },
    wilayah_label: 'Kab. Bogor',
  },
  {
    email: 'op.bandung@dtsen.go.id',
    name: 'Operator Kota Bandung',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Kota Bandung' },
    wilayah_label: 'Kota Bandung',
  },
  {
    email: 'op.tangerang@dtsen.go.id',
    name: 'Operator Kota Tangerang',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Kota Tangerang' },
    wilayah_label: 'Kota Tangerang',
  },
  {
    email: 'op.lebak@dtsen.go.id',
    name: 'Operator Kab. Lebak',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Kab. Lebak' },
    wilayah_label: 'Kab. Lebak',
  },
  {
    email: 'op.semarang@dtsen.go.id',
    name: 'Operator Kota Semarang',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Kota Semarang' },
    wilayah_label: 'Kota Semarang',
  },
  {
    email: 'op.surakarta@dtsen.go.id',
    name: 'Operator Kota Surakarta',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Kota Surakarta' },
    wilayah_label: 'Kota Surakarta',
  },
  {
    email: 'op.surabaya@dtsen.go.id',
    name: 'Operator Kota Surabaya',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Kota Surabaya' },
    wilayah_label: 'Kota Surabaya',
  },
  {
    email: 'op.jakbar@dtsen.go.id',
    name: 'Operator Jakarta Barat',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Jakarta Barat' },
    wilayah_label: 'Jakarta Barat',
  },
  {
    email: 'op.jakut@dtsen.go.id',
    name: 'Operator Jakarta Utara',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Jakarta Utara' },
    wilayah_label: 'Jakarta Utara',
  },
  {
    email: 'op.jaktim@dtsen.go.id',
    name: 'Operator Jakarta Timur',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Jakarta Timur' },
    wilayah_label: 'Jakarta Timur',
  },
  {
    email: 'op.jaksel@dtsen.go.id',
    name: 'Operator Jakarta Selatan',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Jakarta Selatan' },
    wilayah_label: 'Jakarta Selatan',
  },
  {
    email: 'op.jakpus@dtsen.go.id',
    name: 'Operator Jakarta Pusat',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Jakarta Pusat' },
    wilayah_label: 'Jakarta Pusat',
  },
  {
    email: 'op.yogya@dtsen.go.id',
    name: 'Operator Kota Yogyakarta',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Kota Yogyakarta' },
    wilayah_label: 'Kota Yogyakarta',
  },
  {
    email: 'op.bantul@dtsen.go.id',
    name: 'Operator Kab. Bantul',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Kab. Bantul' },
    wilayah_label: 'Kab. Bantul',
  },
  {
    email: 'op.medan@dtsen.go.id',
    name: 'Operator Kota Medan',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Kota Medan' },
    wilayah_label: 'Kota Medan',
  },
  {
    email: 'op.makassar@dtsen.go.id',
    name: 'Operator Kota Makassar',
    role: 'operator',
    wilayah: { level: 'kab_kota', value: 'Kota Makassar' },
    wilayah_label: 'Kota Makassar',
  },
]

// Helper: cari user berdasarkan email (case-insensitive)
export function findUserByEmail(email) {
  return DUMMY_USERS.find(u => u.email.toLowerCase() === email.toLowerCase().trim()) || null
}
