#!/usr/bin/env python3
"""
Script seed TAMBAHAN untuk filter ternak range dropdown.
Aman dijalankan berulang kali (idempotent) — tidak menghapus data lama.

Jalankan:
    cd backend
    python seed_ternak_filter.py

Atau via Docker:
    docker compose exec api python seed_ternak_filter.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db
from app.models.tampilan_dtsen import TampilanDtsen, TampilanDtsenRef

app = create_app()

# 5 field ternak yang akan ditambahkan sebagai filter range dropdown
TERNAK_FIELDS = [
    # (field_key, field_label, urutan)
    ('jumlah_ternak_babi',          'Jumlah Ternak: Babi',           510),
    ('jumlah_ternak_kambing_domba', 'Jumlah Ternak: Kambing / Domba', 520),
    ('jumlah_ternak_kerbau',        'Jumlah Ternak: Kerbau',         530),
    ('jumlah_ternak_kuda',          'Jumlah Ternak: Kuda',           540),
    ('jumlah_ternak_sapi',          'Jumlah Ternak: Sapi',           550),
]

# Opsi range yang akan muncul di dropdown
TERNAK_REFS = [
    ('0',   '0 (Tidak ada)',       1),
    ('1-5', '1 – 5 ekor',         2),
    ('>5',  'Lebih dari 5 ekor',   3),
]


def run():
    with app.app_context():
        added_fields = 0
        added_refs   = 0

        for (field_key, field_label, urutan) in TERNAK_FIELDS:
            # Cek apakah sudah ada
            existing = TampilanDtsen.query.filter_by(field_key=field_key).first()
            if not existing:
                obj = TampilanDtsen(
                    field_key=field_key,
                    field_label=field_label,
                    field_group='Ternak',
                    kategori='keluarga',
                    field_type='Integer',
                    is_filter=1,
                    is_detail=0,
                    is_active=1,
                    urutan=urutan,
                )
                db.session.add(obj)
                db.session.flush()  # agar id terisi
                parent = obj
                added_fields += 1
                print(f"  [+] field baru: {field_key}")
            else:
                # Pastikan is_filter=1 dan field_group=Ternak
                existing.is_filter  = 1
                existing.is_active  = 1
                existing.field_group = 'Ternak'
                db.session.flush()
                parent = existing
                print(f"  [~] field sudah ada, diupdate: {field_key}")

            # Tambahkan refs yang belum ada
            for (ref_value, ref_label, urutan_ref) in TERNAK_REFS:
                exists_ref = TampilanDtsenRef.query.filter_by(
                    tampilan_id=parent.id,
                    ref_value=ref_value
                ).first()
                if not exists_ref:
                    db.session.add(TampilanDtsenRef(
                        tampilan_id=parent.id,
                        ref_value=ref_value,
                        ref_label=ref_label,
                        urutan=urutan_ref,
                    ))
                    added_refs += 1

        db.session.commit()
        print(f"\n[seed_ternak_filter] Selesai: {added_fields} field baru, {added_refs} refs baru ditambahkan.")


if __name__ == '__main__':
    run()
