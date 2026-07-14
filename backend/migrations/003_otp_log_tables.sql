-- Migration: OTP log tables for DTSEN
-- Run once: mysql -u root -p db_simzat < 003_otp_log_tables.sql

CREATE TABLE IF NOT EXISTS `t_log_smtp_dtsen` (
  `id`         INT(11)      NOT NULL AUTO_INCREMENT,
  `user_id`    INT(11)      NOT NULL,
  `user_type`  VARCHAR(20)  NOT NULL,
  `to_email`   VARCHAR(255) NOT NULL,
  `subject`    VARCHAR(255) NOT NULL DEFAULT '',
  `status`     ENUM('sent','failed') NOT NULL DEFAULT 'sent',
  `error_msg`  TEXT         NULL,
  `created_at` TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_user` (`user_id`, `user_type`),
  INDEX `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `t_log_wa_dtsen` (
  `id`         INT(11)      NOT NULL AUTO_INCREMENT,
  `user_id`    INT(11)      NOT NULL,
  `user_type`  VARCHAR(20)  NOT NULL,
  `contact`    VARCHAR(30)  NOT NULL COMMENT 'Nomor WA format 628xxx',
  `status`     ENUM('sent','failed') NOT NULL DEFAULT 'sent',
  `cost`       INT(11)      NOT NULL DEFAULT 650 COMMENT 'Biaya per hit dalam rupiah',
  `error_msg`  TEXT         NULL,
  `created_at` TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_user` (`user_id`, `user_type`),
  INDEX `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
