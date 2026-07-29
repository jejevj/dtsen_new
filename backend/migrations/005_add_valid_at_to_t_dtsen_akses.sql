-- Migration 005: Tambah kolom valid_from_at dan valid_until_at ke t_dtsen_akses
-- Fix: AttributeError 'TDtsenAkses' object has no attribute 'valid_from_at'
--      yang terjadi di auth_service.py saat login POST /api/v1/auth/login
-- Date: 2026-07-29

ALTER TABLE t_dtsen_akses
    ADD COLUMN valid_from_at  DATETIME NULL COMMENT 'Tanggal mulai akses aktif'
        AFTER activated_at,
    ADD COLUMN valid_until_at DATETIME NULL COMMENT 'Tanggal berakhir akses'
        AFTER valid_from_at;
