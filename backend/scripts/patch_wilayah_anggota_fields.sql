-- =============================================================================
-- PATCH: Tambah field Wilayah/Alamat KTP untuk ZawaAnggota (individu)
-- Tabel : m_tampilan_dtsen
-- Alasan: Seed awal mendaftarkan key fiktif (provinsi_kode, kabkota_kode, dll)
--         yang tidak cocok dengan kolom nyata di zawa_anggota.
--         Script ini mengganti/melengkapi group "Wilayah" agar field key
--         sesuai dengan kolom di tabel zawa_anggota.
--
-- Cara pakai:
--   docker compose exec db mysql -u<user> -p<pass> <dbname> < patch_wilayah_anggota_fields.sql
--   atau jalankan langsung di MySQL client.
-- =============================================================================

-- 1. Hapus field lama group Wilayah individu yang key-nya tidak cocok
DELETE FROM m_tampilan_dtsen
WHERE kategori IN ('individu', 'keduanya')
  AND field_group = 'Wilayah'
  AND field_key IN (
    'provinsi_kode',
    'kabkota_kode',
    'kecamatan_kode',
    'kelurahan_kode'
  );

-- 2. Insert field Wilayah yang sesuai kolom zawa_anggota
--    Gunakan INSERT IGNORE agar aman jika sudah ada sebagian.
INSERT IGNORE INTO m_tampilan_dtsen
    (field_key,              field_label,        field_group, kategori,   field_type, is_filter, is_detail, is_active, urutan)
VALUES
    ('alamat_ktp',           'Alamat KTP',       'Wilayah',   'individu', 'String',   0,         1,         1,         100),
    ('dusun_ktp',            'Dusun',            'Wilayah',   'individu', 'String',   0,         1,         1,         105),
    ('rt_ktp',               'RT',               'Wilayah',   'individu', 'String',   0,         1,         1,         110),
    ('rw_ktp',               'RW',               'Wilayah',   'individu', 'String',   0,         1,         1,         115),
    ('kelurahan_desa_ktp',   'Kelurahan/Desa',   'Wilayah',   'individu', 'String',   1,         1,         1,         120),
    ('kecamatan_ktp',        'Kecamatan',        'Wilayah',   'individu', 'String',   1,         1,         1,         130),
    ('kabupaten_kota_ktp',   'Kab/Kota',         'Wilayah',   'individu', 'String',   1,         1,         1,         140),
    ('provinsi_ktp',         'Provinsi',         'Wilayah',   'individu', 'String',   1,         1,         1,         150);

-- 3. Verifikasi hasil
SELECT id, field_key, field_label, field_group, kategori, is_detail, urutan
FROM   m_tampilan_dtsen
WHERE  field_group = 'Wilayah'
  AND  kategori IN ('individu', 'keduanya')
ORDER  BY urutan;
