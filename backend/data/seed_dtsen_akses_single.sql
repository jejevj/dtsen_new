-- =============================================================
-- Seed MINIMAL: satu baris t_dtsen_akses (laz_kode LAZ20240226DELQ)
-- Cocok untuk insert cepat / testing satu pengguna saja
-- Password: MD5('Dtsen@2026!')
-- =============================================================

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
    'LAZ20240226DELQ',   -- laz_kode
    '3201010101900001',  -- NIK (ganti sesuai data asli)
    'Nama Lengkap',      -- nama_lengkap
    '1990-01-01',        -- lahir_tanggal
    'L',                 -- gender: L / P
    '081200000000',      -- notelp
    'pengguna@lazdelq.org', -- email
    'Koordinator LAZ',   -- jabatan
    'aktif',             -- statuses
    MD5('Dtsen@2026!'),  -- password (MD5)
    NOW()                -- created_at
);
