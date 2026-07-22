-- ============================================================
-- Migration: Tambah filter desil_nasional untuk tab Keluarga
-- Tabel: m_tampilan_dtsen + m_tampilan_dtsen_ref
-- Jalankan sekali saja di database produksi / staging
-- ============================================================

-- 1. Insert row master (lewati jika sudah ada)
INSERT INTO m_tampilan_dtsen
  (field_key, field_label, field_group, kategori, field_type, is_filter, is_detail, is_active, urutan)
SELECT
  'desil_nasional',
  'Desil Kemiskinan',
  'Kesejahteraan',
  'keluarga',
  'String',
  1,   -- is_filter = aktif
  1,   -- is_detail = tampil di halaman detail
  1,   -- is_active
  910  -- urutan: setelah pbi_nas (biasanya 900)
WHERE NOT EXISTS (
  SELECT 1 FROM m_tampilan_dtsen WHERE field_key = 'desil_nasional'
);

-- 2. Insert refs Desil 1-10 + Desil 0 (tidak diketahui)
--    Gunakan INSERT IGNORE agar idempoten
SET @tid = (SELECT id FROM m_tampilan_dtsen WHERE field_key = 'desil_nasional' LIMIT 1);

INSERT IGNORE INTO m_tampilan_dtsen_ref (tampilan_id, ref_value, ref_label, urutan) VALUES
  (@tid, '0',  'Desil 0 – Tidak Diketahui',   0),
  (@tid, '1',  'Desil 1 – Sangat Miskin',       1),
  (@tid, '2',  'Desil 2 – Miskin',              2),
  (@tid, '3',  'Desil 3 – Hampir Miskin',       3),
  (@tid, '4',  'Desil 4 – Rentan Miskin',       4),
  (@tid, '5',  'Desil 5',                        5),
  (@tid, '6',  'Desil 6',                        6),
  (@tid, '7',  'Desil 7',                        7),
  (@tid, '8',  'Desil 8',                        8),
  (@tid, '9',  'Desil 9',                        9),
  (@tid, '10', 'Desil 10 – Tidak Miskin',       10);

-- Selesai. Verifikasi:
-- SELECT td.field_key, td.kategori, td.is_filter, COUNT(r.id) AS jumlah_refs
-- FROM m_tampilan_dtsen td
-- LEFT JOIN m_tampilan_dtsen_ref r ON r.tampilan_id = td.id
-- WHERE td.field_key = 'desil_nasional'
-- GROUP BY td.id;
