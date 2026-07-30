-- =============================================================
-- Migration: Buat tabel cache ZAWA
-- Field disesuaikan dengan response nyata ZAWA API
-- Jalankan sekali:
--   mysql -u user -p db_simzat < backend/migrations/zawa_tables.sql
-- =============================================================

CREATE TABLE IF NOT EXISTS `zawa_anggota` (
    `id`                         BIGINT       NOT NULL AUTO_INCREMENT,
    -- Identitas
    `nomor_induk_kependudukan`   VARCHAR(20)  DEFAULT NULL,
    `nomor_kartu_keluarga`       VARCHAR(20)  DEFAULT NULL,
    `nama`                       VARCHAR(255) DEFAULT NULL,
    `jenis_kelamin`              VARCHAR(5)   DEFAULT NULL,
    `tanggal_lahir`              DATE         DEFAULT NULL,
    `status_kawin`               VARCHAR(5)   DEFAULT NULL,
    `status_hubungan_keluarga`   VARCHAR(5)   DEFAULT NULL,
    -- Alamat KTP
    `alamat_ktp`                 TEXT         DEFAULT NULL,
    `dusun_ktp`                  VARCHAR(100) DEFAULT NULL,
    `rt_ktp`                     INT          DEFAULT NULL,
    `rw_ktp`                     INT          DEFAULT NULL,
    `kelurahan_desa_ktp`         VARCHAR(100) DEFAULT NULL,
    `kecamatan_ktp`              VARCHAR(100) DEFAULT NULL,
    `kabupaten_kota_ktp`         VARCHAR(100) DEFAULT NULL,
    `provinsi_ktp`               VARCHAR(100) DEFAULT NULL,
    `kode_provinsi_ktp`          VARCHAR(10)  DEFAULT NULL,
    `kode_kabupaten_kota_ktp`    VARCHAR(10)  DEFAULT NULL,
    `kode_kecamatan_ktp`         VARCHAR(10)  DEFAULT NULL,
    `kode_kelurahan_desa_ktp`    VARCHAR(15)  DEFAULT NULL,
    -- Pendidikan
    `partisipasi_sekolah`                VARCHAR(5) DEFAULT NULL,
    `jenjang_tertinggi_yang_diduduki`    INT        DEFAULT NULL,
    `kelas_tertinggi_yang_diduduki`      INT        DEFAULT NULL,
    `ijazah_tertinggi_yang_dimiliki`     INT        DEFAULT NULL,
    -- Pekerjaan
    `status_bekerja`                                   VARCHAR(5)     DEFAULT NULL,
    `status_dalam_pekerjaan_utama`                     VARCHAR(5)     DEFAULT NULL,
    `lapangan_usaha_dari_pekerjaan_utama`               INT            DEFAULT NULL,
    `lapangan_usaha_dari_usaha_utama`                   INT            DEFAULT NULL,
    `kepemilikan_usaha`                                VARCHAR(5)     DEFAULT NULL,
    `jumlah_usaha`                                     INT            DEFAULT NULL,
    `jumlah_pekerja_yang_dibayar_dari_usaha_utama`     INT            DEFAULT NULL,
    `jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama` INT          DEFAULT NULL,
    `omzet_usaha_utama`                                DECIMAL(15,2)  DEFAULT NULL,
    `id_pelanggan_pln`                                 VARCHAR(20)    DEFAULT NULL,
    -- Kesehatan & disabilitas
    `kondisi_gizi`               VARCHAR(5) DEFAULT NULL,
    `penyakit_kronis`            INT        DEFAULT NULL,
    `penglihatan`                VARCHAR(5) DEFAULT NULL,
    `pendengaran`                VARCHAR(5) DEFAULT NULL,
    `berjalan_atau_naik_tangga`  VARCHAR(5) DEFAULT NULL,
    `menggunakan_tangan_jari`    VARCHAR(5) DEFAULT NULL,
    `mengingat_berkonsentrasi`   VARCHAR(5) DEFAULT NULL,
    `berbicara_komunikasi`       VARCHAR(5) DEFAULT NULL,
    `belajar_kemampuan_intelektual` VARCHAR(5) DEFAULT NULL,
    `mengurus_diri`              VARCHAR(5) DEFAULT NULL,
    `kesedihan_depresi`          VARCHAR(5) DEFAULT NULL,
    `pengendalian_perilaku`      VARCHAR(5) DEFAULT NULL,
    -- Bansos
    `pbi_nas`    VARCHAR(5) DEFAULT NULL,
    `pbi_pemda`  VARCHAR(5) DEFAULT NULL,
    -- Raw & metadata
    `raw_data`      JSON     DEFAULT NULL,
    `provinsi_slug` VARCHAR(20)  DEFAULT NULL,
    `synced_at`     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `created_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_anggota_nik`              (`nomor_induk_kependudukan`),
    INDEX `idx_anggota_nkk`              (`nomor_kartu_keluarga`),
    INDEX `idx_anggota_provinsi_slug`    (`provinsi_slug`),
    INDEX `idx_anggota_slug_nik`         (`provinsi_slug`, `nomor_induk_kependudukan`),
    INDEX `idx_anggota_slug_nkk`         (`provinsi_slug`, `nomor_kartu_keluarga`),
    -- Index wilayah KTP (individual) — untuk filter per level
    INDEX `idx_anggota_kode_provinsi_ktp` (`kode_provinsi_ktp`),
    INDEX `idx_anggota_kode_kabkota_ktp`  (`kode_kabupaten_kota_ktp`),
    INDEX `idx_anggota_kode_kecamatan_ktp`(`kode_kecamatan_ktp`),
    INDEX `idx_anggota_kode_kel_ktp`      (`kode_kelurahan_desa_ktp`),
    -- Index composite wilayah KTP — untuk query bertingkat (paling efisien)
    INDEX `idx_anggota_wilayah_ktp`       (`kode_provinsi_ktp`, `kode_kabupaten_kota_ktp`, `kode_kecamatan_ktp`, `kode_kelurahan_desa_ktp`),
    FULLTEXT INDEX `ft_anggota_nama`     (`nama`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS `zawa_keluarga` (
    `id`                     BIGINT       NOT NULL AUTO_INCREMENT,
    -- Identitas
    `nomor_kartu_keluarga`   VARCHAR(20)  DEFAULT NULL,
    `nama_anggota_keluarga`  VARCHAR(255) DEFAULT NULL,
    `jumlah_anggota_keluarga` INT         DEFAULT NULL,
    -- Alamat
    `alamat`             TEXT         DEFAULT NULL,
    `kelurahan_desa`     VARCHAR(100) DEFAULT NULL,
    `kecamatan`          VARCHAR(100) DEFAULT NULL,
    `kabupaten_kota`     VARCHAR(100) DEFAULT NULL,
    `provinsi`           VARCHAR(100) DEFAULT NULL,
    `kode_provinsi`      VARCHAR(10)  DEFAULT NULL,
    `kode_kabupaten_kota`  VARCHAR(10)  DEFAULT NULL,
    `kode_kecamatan`     VARCHAR(10)  DEFAULT NULL,
    `kode_kelurahan_desa`  VARCHAR(15)  DEFAULT NULL,
    -- Kondisi rumah
    `luas_lantai`               INT        DEFAULT NULL,
    `jenis_lantai_terluas`      INT        DEFAULT NULL,
    `jenis_dinding_terluas`     INT        DEFAULT NULL,
    `jenis_atap_terluas`        INT        DEFAULT NULL,
    `status_kepemilikan_rumah`  VARCHAR(5) DEFAULT NULL,
    `fasilitas_bab`             VARCHAR(5) DEFAULT NULL,
    `jenis_kloset`              VARCHAR(5) DEFAULT NULL,
    `pembuangan_akhir_tinja`    VARCHAR(5) DEFAULT NULL,
    `sumber_air_minum_utama`    INT        DEFAULT NULL,
    `sumber_penerangan_utama`   VARCHAR(5) DEFAULT NULL,
    `bahan_bakar_utama_memasak` INT        DEFAULT NULL,
    `daya_terpasang`            INT        DEFAULT NULL,
    `id_pelanggan_pln`          VARCHAR(20) DEFAULT NULL,
    -- Aset bergerak
    `aset_bergerak_sepeda_motor`           VARCHAR(5) DEFAULT NULL,
    `aset_bergerak_mobil`                  VARCHAR(5) DEFAULT NULL,
    `aset_bergerak_sepeda`                 VARCHAR(5) DEFAULT NULL,
    `aset_bergerak_perahu`                 VARCHAR(5) DEFAULT NULL,
    `aset_bergerak_kapal_perahu_motor`     VARCHAR(5) DEFAULT NULL,
    `aset_bergerak_smartphone`             VARCHAR(5) DEFAULT NULL,
    `aset_bergerak_komputer_laptop_tablet` VARCHAR(5) DEFAULT NULL,
    `aset_bergerak_tv_datar`               VARCHAR(5) DEFAULT NULL,
    `aset_bergerak_lemari_es`              VARCHAR(5) DEFAULT NULL,
    `aset_bergerak_ac`                     VARCHAR(5) DEFAULT NULL,
    `aset_bergerak_pemanas_air`            VARCHAR(5) DEFAULT NULL,
    `aset_bergerak_tabung_gas`             VARCHAR(5) DEFAULT NULL,
    `aset_bergerak_telepon_rumah`          VARCHAR(5) DEFAULT NULL,
    `aset_bergerak_emas_perhiasan`         VARCHAR(5) DEFAULT NULL,
    -- Aset tidak bergerak
    `aset_tidak_bergerak_rumah_lainnya`  VARCHAR(5) DEFAULT NULL,
    `aset_tidak_bergerak_lahan_lainnya`  VARCHAR(5) DEFAULT NULL,
    `kepemilikan_aset`                   VARCHAR(5) DEFAULT NULL,
    -- Ternak
    `jumlah_ternak_sapi`           INT DEFAULT NULL,
    `jumlah_ternak_kerbau`         INT DEFAULT NULL,
    `jumlah_ternak_kuda`           INT DEFAULT NULL,
    `jumlah_ternak_kambing_domba`  INT DEFAULT NULL,
    `jumlah_ternak_babi`           INT DEFAULT NULL,
    -- Bansos & kesejahteraan
    `pbi_nas`        VARCHAR(5) DEFAULT NULL,
    `pbi_pemda`      VARCHAR(5) DEFAULT NULL,
    `desil_nasional` VARCHAR(5) DEFAULT NULL,
    -- Raw & metadata
    `raw_data`   JSON     DEFAULT NULL,
    `synced_at`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `idx_keluarga_nkk_unik`      (`nomor_kartu_keluarga`),
    INDEX        `idx_keluarga_provinsi`       (`provinsi`),
    INDEX        `idx_keluarga_kode_provinsi`  (`kode_provinsi`),
    -- Index wilayah (individual) — untuk filter per level
    INDEX        `idx_keluarga_kode_kabkota`   (`kode_kabupaten_kota`),
    INDEX        `idx_keluarga_kode_kecamatan` (`kode_kecamatan`),
    INDEX        `idx_keluarga_kode_kelurahan` (`kode_kelurahan_desa`),
    -- Index composite wilayah — untuk query bertingkat (paling efisien)
    INDEX        `idx_keluarga_wilayah`        (`kode_provinsi`, `kode_kabupaten_kota`, `kode_kecamatan`, `kode_kelurahan_desa`),
    FULLTEXT INDEX `ft_keluarga_nama_alamat`   (`nama_anggota_keluarga`, `alamat`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS `zawa_sync_log` (
    `id`            BIGINT      NOT NULL AUTO_INCREMENT,
    `sync_type`     VARCHAR(20) NOT NULL,
    `provinsi_slug` VARCHAR(20) DEFAULT NULL,
    `status`        VARCHAR(10) NOT NULL DEFAULT 'running',
    `total_fetched` INT         DEFAULT 0,
    `total_saved`   INT         DEFAULT 0,
    `error_message` TEXT        DEFAULT NULL,
    `started_at`    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `finished_at`   DATETIME    DEFAULT NULL,
    PRIMARY KEY (`id`),
    INDEX `idx_synclog_type_status` (`sync_type`, `status`),
    INDEX `idx_synclog_started`     (`started_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
