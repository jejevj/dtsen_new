-- ============================================================
-- SEED: data awal m_tampilan_dtsen & m_tampilan_dtsen_ref
-- Sesuaikan field_key dengan key yang dikembalikan API DTSEN
-- ============================================================

-- Kosongkan dulu agar idempotent (aman dijalankan ulang)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE `m_tampilan_dtsen_ref`;
TRUNCATE TABLE `m_tampilan_dtsen`;
SET FOREIGN_KEY_CHECKS = 1;

-- ── Identitas Dasar ─────────────────────────────────────────
INSERT INTO `m_tampilan_dtsen`
  (field_key, field_label, field_group, kategori, field_type, is_filter, is_detail, is_active, urutan)
VALUES
  ('nama_lengkap',   'Nama Lengkap',    'Identitas', 'individu', 'String',       1, 1, 1, 10),
  ('nik',            'NIK',             'Identitas', 'individu', 'String',       1, 1, 1, 20),
  ('jenis_kelamin',  'Jenis Kelamin',   'Identitas', 'individu', 'String (kode)',1, 1, 1, 30),
  ('lahir_tanggal',  'Tanggal Lahir',   'Identitas', 'individu', 'Date',         0, 1, 1, 40),
  ('agama',          'Agama',           'Identitas', 'individu', 'String (kode)',1, 1, 1, 50),

-- ── Penerimaan ──────────────────────────────────────────────
  ('laz_kode',       'LAZ',             'Penerimaan','individu', 'String',       1, 1, 1, 60),
  ('program_kode',   'Program',         'Penerimaan','individu', 'String',       1, 1, 1, 70),
  ('tipe_penerimaan','Tipe Penerimaan', 'Penerimaan','individu', 'String (kode)',1, 1, 1, 80),
  ('tanggal_terima', 'Tanggal Terima',  'Penerimaan','individu', 'Date',         1, 1, 1, 90),

-- ── Wilayah Domisili ────────────────────────────────────────
  ('provinsi_kode',  'Provinsi',        'Wilayah',   'individu', 'String',       1, 1, 1, 100),
  ('kabkota_kode',   'Kab/Kota',        'Wilayah',   'individu', 'String',       1, 1, 1, 110),
  ('kecamatan_kode', 'Kecamatan',       'Wilayah',   'individu', 'String',       0, 1, 1, 120),
  ('kelurahan_kode', 'Kelurahan',       'Wilayah',   'individu', 'String',       0, 1, 1, 130);


-- ── Refs: Jenis Kelamin ──────────────────────────────────────
INSERT INTO `m_tampilan_dtsen_ref` (tampilan_id, ref_value, ref_label, urutan)
SELECT id, 'm', 'Laki-laki', 1 FROM `m_tampilan_dtsen` WHERE field_key = 'jenis_kelamin'
UNION ALL
SELECT id, 'f', 'Perempuan', 2 FROM `m_tampilan_dtsen` WHERE field_key = 'jenis_kelamin';

-- ── Refs: Agama ──────────────────────────────────────────────
INSERT INTO `m_tampilan_dtsen_ref` (tampilan_id, ref_value, ref_label, urutan)
SELECT id, 'Islam',     'Islam',     1 FROM `m_tampilan_dtsen` WHERE field_key = 'agama'
UNION ALL
SELECT id, 'Kristen',   'Kristen',   2 FROM `m_tampilan_dtsen` WHERE field_key = 'agama'
UNION ALL
SELECT id, 'Katolik',   'Katolik',   3 FROM `m_tampilan_dtsen` WHERE field_key = 'agama'
UNION ALL
SELECT id, 'Hindu',     'Hindu',     4 FROM `m_tampilan_dtsen` WHERE field_key = 'agama'
UNION ALL
SELECT id, 'Buddha',    'Buddha',    5 FROM `m_tampilan_dtsen` WHERE field_key = 'agama'
UNION ALL
SELECT id, 'Konghucu',  'Konghucu',  6 FROM `m_tampilan_dtsen` WHERE field_key = 'agama';

-- ── Refs: Tipe Penerimaan ────────────────────────────────────
INSERT INTO `m_tampilan_dtsen_ref` (tampilan_id, ref_value, ref_label, urutan)
SELECT id, 'pml',  'Langsung',       1 FROM `m_tampilan_dtsen` WHERE field_key = 'tipe_penerimaan'
UNION ALL
SELECT id, 'pmtl', 'Tidak Langsung', 2 FROM `m_tampilan_dtsen` WHERE field_key = 'tipe_penerimaan';
