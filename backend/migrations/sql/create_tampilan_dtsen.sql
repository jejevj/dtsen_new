-- ============================================================
-- DDL: m_tampilan_dtsen + m_tampilan_dtsen_ref
-- Jalankan sekali di database db_simzat_haha
-- ============================================================

CREATE TABLE IF NOT EXISTS `m_tampilan_dtsen` (
  `id`          INT            NOT NULL AUTO_INCREMENT,
  `field_key`   VARCHAR(100)   NOT NULL COMMENT 'Nama key dari API DTSEN, unik',
  `field_label` VARCHAR(200)   NOT NULL COMMENT 'Label kolom yang ditampilkan ke user',
  `field_group` VARCHAR(100)   NOT NULL DEFAULT '' COMMENT 'Grup/seksi field',
  `kategori`    ENUM('individu','keluarga') NOT NULL DEFAULT 'individu',
  `field_type`  VARCHAR(50)    NOT NULL DEFAULT 'String' COMMENT 'String, String (kode), Integer, Float, Date',
  `is_filter`   TINYINT(1)     NOT NULL DEFAULT 0 COMMENT '1 = bisa dijadikan filter pencarian',
  `is_detail`   TINYINT(1)     NOT NULL DEFAULT 0 COMMENT '1 = tampil di halaman detail individu',
  `is_active`   TINYINT(1)     NOT NULL DEFAULT 1,
  `urutan`      INT            NOT NULL DEFAULT 0 COMMENT 'Urutan tampil kolom',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_field_key` (`field_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS `m_tampilan_dtsen_ref` (
  `id`          INT           NOT NULL AUTO_INCREMENT,
  `tampilan_id` INT           NOT NULL COMMENT 'FK ke m_tampilan_dtsen.id',
  `ref_value`   VARCHAR(50)   NOT NULL COMMENT 'Nilai/kode dari API',
  `ref_label`   VARCHAR(200)  NOT NULL COMMENT 'Keterangan nilai',
  `urutan`      INT           NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_tampilan_ref_value` (`tampilan_id`, `ref_value`),
  CONSTRAINT `fk_tampilan_dtsen_ref`
    FOREIGN KEY (`tampilan_id`) REFERENCES `m_tampilan_dtsen` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
