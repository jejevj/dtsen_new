-- =============================================================
-- Migration: Tambah index wilayah pada tabel yang sudah ada
-- Jalankan pada DB yang sudah running (tabel sudah ada isinya):
--   mysql -u user -p db_simzat < backend/migrations/add_wilayah_indexes.sql
--
-- Catatan: ALTER TABLE pada tabel besar bisa memakan waktu.
-- Gunakan pt-online-schema-change jika tabel > 10 juta baris.
-- =============================================================

-- -------------------------------------------------------
-- zawa_anggota: index wilayah KTP
-- -------------------------------------------------------

-- Index individual — dipakai saat hanya filter 1 level
ALTER TABLE `zawa_anggota`
    ADD INDEX IF NOT EXISTS `idx_anggota_kode_provinsi_ktp`  (`kode_provinsi_ktp`),
    ADD INDEX IF NOT EXISTS `idx_anggota_kode_kabkota_ktp`   (`kode_kabupaten_kota_ktp`),
    ADD INDEX IF NOT EXISTS `idx_anggota_kode_kecamatan_ktp` (`kode_kecamatan_ktp`),
    ADD INDEX IF NOT EXISTS `idx_anggota_kode_kel_ktp`       (`kode_kelurahan_desa_ktp`);

-- Index composite wilayah KTP — mencakup semua kombinasi filter bertingkat.
-- MySQL dapat memanfaatkan prefix dari composite index, artinya:
--   WHERE kode_provinsi_ktp = ?                                          → pakai index ini
--   WHERE kode_provinsi_ktp = ? AND kode_kabupaten_kota_ktp = ?          → pakai index ini
--   WHERE kode_provinsi_ktp = ? AND ... AND kode_kecamatan_ktp = ?       → pakai index ini
--   WHERE kode_provinsi_ktp = ? AND ... AND kode_kelurahan_desa_ktp = ?  → pakai index ini
ALTER TABLE `zawa_anggota`
    ADD INDEX IF NOT EXISTS `idx_anggota_wilayah_ktp` (
        `kode_provinsi_ktp`,
        `kode_kabupaten_kota_ktp`,
        `kode_kecamatan_ktp`,
        `kode_kelurahan_desa_ktp`
    );

-- -------------------------------------------------------
-- zawa_keluarga: index wilayah
-- -------------------------------------------------------

-- Index individual
ALTER TABLE `zawa_keluarga`
    ADD INDEX IF NOT EXISTS `idx_keluarga_kode_kabkota`   (`kode_kabupaten_kota`),
    ADD INDEX IF NOT EXISTS `idx_keluarga_kode_kecamatan` (`kode_kecamatan`),
    ADD INDEX IF NOT EXISTS `idx_keluarga_kode_kelurahan` (`kode_kelurahan_desa`);

-- Index composite wilayah
ALTER TABLE `zawa_keluarga`
    ADD INDEX IF NOT EXISTS `idx_keluarga_wilayah` (
        `kode_provinsi`,
        `kode_kabupaten_kota`,
        `kode_kecamatan`,
        `kode_kelurahan_desa`
    );
