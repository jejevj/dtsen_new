-- =============================================================
-- Seed: t_dtsen_akses — pengguna DTSEN untuk LAZ20240226DELQ
-- Password: MD5('Dtsen@2026!')
-- Jalankan setelah tabel t_dtsen_akses sudah dibuat (flask db upgrade)
-- =============================================================

-- Nonaktifkan foreign key check sementara (opsional jika ada FK)
SET FOREIGN_KEY_CHECKS = 0;

-- -------------------------------------------------------------
-- 1. Koordinator / Admin LAZ  (jabatan: Koordinator LAZ)
-- -------------------------------------------------------------
INSERT INTO `t_dtsen_akses` (
    `laz_kode`,
    `nik`,
    `nama_lengkap`,
    `lahir_tanggal`,
    `gender`,
    `notelp`,
    `email`,
    `jabatan`,
    `statuses`,
    `dtsen_akses_password`,
    `created_at`
) VALUES (
    'LAZ20240226DELQ',
    '3201010101900001',
    'Koordinator LAZ DELQ',
    '1990-01-01',
    'L',
    '081200000001',
    'koordinator@lazdelq.org',
    'Koordinator LAZ',
    'aktif',
    MD5('Dtsen@2026!'),
    NOW()
);

-- -------------------------------------------------------------
-- 2. Petugas Verifikasi  (jabatan: Petugas Verifikasi)
-- -------------------------------------------------------------
INSERT INTO `t_dtsen_akses` (
    `laz_kode`,
    `nik`,
    `nama_lengkap`,
    `lahir_tanggal`,
    `gender`,
    `notelp`,
    `email`,
    `jabatan`,
    `statuses`,
    `dtsen_akses_password`,
    `created_at`
) VALUES (
    'LAZ20240226DELQ',
    '3201010101920002',
    'Petugas Verifikasi LAZ DELQ',
    '1992-03-15',
    'P',
    '081200000002',
    'verifikasi@lazdelq.org',
    'Petugas Verifikasi',
    'aktif',
    MD5('Dtsen@2026!'),
    NOW()
);

-- -------------------------------------------------------------
-- 3. Petugas Lapangan  (jabatan: Petugas Lapangan)
-- -------------------------------------------------------------
INSERT INTO `t_dtsen_akses` (
    `laz_kode`,
    `nik`,
    `nama_lengkap`,
    `lahir_tanggal`,
    `gender`,
    `notelp`,
    `email`,
    `jabatan`,
    `statuses`,
    `dtsen_akses_password`,
    `created_at`
) VALUES (
    'LAZ20240226DELQ',
    '3201010101950003',
    'Petugas Lapangan LAZ DELQ',
    '1995-07-20',
    'L',
    '081200000003',
    'lapangan@lazdelq.org',
    'Petugas Lapangan',
    'aktif',
    MD5('Dtsen@2026!'),
    NOW()
);

-- -------------------------------------------------------------
-- Aktifkan kembali foreign key check
-- -------------------------------------------------------------
SET FOREIGN_KEY_CHECKS = 1;

-- -------------------------------------------------------------
-- Verifikasi hasil insert
-- -------------------------------------------------------------
SELECT
    dtsen_akses_id,
    laz_kode,
    nik,
    nama_lengkap,
    jabatan,
    statuses,
    created_at
FROM t_dtsen_akses
WHERE laz_kode = 'LAZ20240226DELQ'
ORDER BY dtsen_akses_id;
