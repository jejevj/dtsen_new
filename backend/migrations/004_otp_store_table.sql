-- Migration: OTP persistent store
-- Run once: mysql -u root -p db_simzat < 004_otp_store_table.sql

CREATE TABLE IF NOT EXISTS `t_otp_dtsen` (
  `id`         INT(11)      NOT NULL AUTO_INCREMENT,
  `otp_key`    VARCHAR(100) NOT NULL COMMENT 'Format: otp_email_{id}_{type} atau otp_wa_{id}_{type}',
  `code`       VARCHAR(10)  NOT NULL,
  `expires_at` DATETIME     NOT NULL,
  `used`       TINYINT(1)   NOT NULL DEFAULT 0,
  `created_at` TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_otp_key` (`otp_key`),
  INDEX `idx_expires` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
