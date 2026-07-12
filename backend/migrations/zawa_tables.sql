-- =============================================================
-- Migration: Buat tabel cache ZAWA
-- Jalankan sekali di database production:
--   mysql -u user -p db_simzat < migrations/zawa_tables.sql
-- =============================================================

CREATE TABLE IF NOT EXISTS `zawa_anggota` (
    `id`                       BIGINT        NOT NULL AUTO_INCREMENT,
    `nomor_induk_kependudukan` VARCHAR(16)   DEFAULT NULL,
    `nomor_kartu_keluarga`     VARCHAR(16)   DEFAULT NULL,
    `nama`                     VARCHAR(255)  DEFAULT NULL,
    `jenis_kelamin`            VARCHAR(10)   DEFAULT NULL,
    `tanggal_lahir`            DATE          DEFAULT NULL,
    `tempat_lahir`             VARCHAR(100)  DEFAULT NULL,
    `agama`                    VARCHAR(50)   DEFAULT NULL,
    `status_perkawinan`        VARCHAR(50)   DEFAULT NULL,
    `hubungan_keluarga`        VARCHAR(50)   DEFAULT NULL,
    `alamat`                   TEXT          DEFAULT NULL,
    `rt`                       VARCHAR(5)    DEFAULT NULL,
    `rw`                       VARCHAR(5)    DEFAULT NULL,
    `kelurahan`                VARCHAR(100)  DEFAULT NULL,
    `kecamatan`                VARCHAR(100)  DEFAULT NULL,
    `kabupaten_kota`           VARCHAR(100)  DEFAULT NULL,
    `provinsi`                 VARCHAR(100)  DEFAULT NULL,
    `kode_pos`                 VARCHAR(10)   DEFAULT NULL,
    `penghasilan`              INT           DEFAULT NULL,
    `pekerjaan`                VARCHAR(100)  DEFAULT NULL,
    `pendidikan`               VARCHAR(100)  DEFAULT NULL,
    `raw_data`                 JSON          DEFAULT NULL,
    `provinsi_slug`            VARCHAR(20)   DEFAULT NULL,
    `synced_at`                DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `created_at`               DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`               DATETIME      DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX  `idx_anggota_nik`             (`nomor_induk_kependudukan`),
    INDEX  `idx_anggota_nkk`             (`nomor_kartu_keluarga`),
    INDEX  `idx_anggota_provinsi`        (`provinsi`),
    INDEX  `idx_anggota_provinsi_slug`   (`provinsi_slug`),
    INDEX  `idx_anggota_provinsi_nik`    (`provinsi_slug`, `nomor_induk_kependudukan`),
    INDEX  `idx_anggota_provinsi_nkk`    (`provinsi_slug`, `nomor_kartu_keluarga`),
    FULLTEXT INDEX `ft_anggota_nama_alamat` (`nama`, `alamat`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS `zawa_keluarga` (
    `id`                   BIGINT        NOT NULL AUTO_INCREMENT,
    `nomor_kartu_keluarga` VARCHAR(16)   DEFAULT NULL,
    `kepala_keluarga`      VARCHAR(255)  DEFAULT NULL,
    `jumlah_anggota`       INT           DEFAULT NULL,
    `alamat`               TEXT          DEFAULT NULL,
    `rt`                   VARCHAR(5)    DEFAULT NULL,
    `rw`                   VARCHAR(5)    DEFAULT NULL,
    `kelurahan`            VARCHAR(100)  DEFAULT NULL,
    `kecamatan`            VARCHAR(100)  DEFAULT NULL,
    `kabupaten_kota`       VARCHAR(100)  DEFAULT NULL,
    `provinsi`             VARCHAR(100)  DEFAULT NULL,
    `kode_pos`             VARCHAR(10)   DEFAULT NULL,
    `raw_data`             JSON          DEFAULT NULL,
    `synced_at`            DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `created_at`           DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`           DATETIME      DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `idx_keluarga_nkk_unik`     (`nomor_kartu_keluarga`),
    INDEX        `idx_keluarga_provinsi`      (`provinsi`),
    FULLTEXT INDEX `ft_keluarga_nama_alamat`  (`kepala_keluarga`, `alamat`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS `zawa_sync_log` (
    `id`            BIGINT       NOT NULL AUTO_INCREMENT,
    `sync_type`     VARCHAR(20)  NOT NULL,
    `provinsi_slug` VARCHAR(20)  DEFAULT NULL,
    `status`        VARCHAR(10)  NOT NULL DEFAULT 'running',
    `total_fetched` INT          DEFAULT 0,
    `total_saved`   INT          DEFAULT 0,
    `error_message` TEXT         DEFAULT NULL,
    `started_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `finished_at`   DATETIME     DEFAULT NULL,
    PRIMARY KEY (`id`),
    INDEX `idx_synclog_type_status` (`sync_type`, `status`),
    INDEX `idx_synclog_started`     (`started_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
