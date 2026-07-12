#!/usr/bin/env python3
"""
Script seed tabel m_tampilan_dtsen & m_tampilan_dtsen_ref.
Jalankan SATU KALI setelah tabel dibuat:

    cd backend
    python seed_tampilan_dtsen.py

Atau via Docker:
    docker compose exec api python seed_tampilan_dtsen.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db
from app.models.tampilan_dtsen import TampilanDtsen, TampilanDtsenRef

app = create_app()


def run():
    with app.app_context():
        # Buat tabel jika belum ada (idempotent)
        db.create_all()
        print("[seed] Tabel sudah siap.")

        # Hapus data lama agar seed bisa dijalankan ulang
        TampilanDtsenRef.query.delete()
        TampilanDtsen.query.delete()
        db.session.commit()
        print("[seed] Data lama dihapus.")

        # ── Field definitions ───────────────────────────────────────
        fields = [
            # (field_key, field_label, field_group, kategori, field_type, is_filter, is_detail, urutan)
            # Identitas
            ('nama_lengkap',    'Nama Lengkap',    'Identitas',  'individu', 'String',        True,  True,  10),
            ('nik',             'NIK',             'Identitas',  'individu', 'String',        True,  True,  20),
            ('jenis_kelamin',   'Jenis Kelamin',   'Identitas',  'individu', 'String (kode)', True,  True,  30),
            ('lahir_tanggal',   'Tanggal Lahir',   'Identitas',  'individu', 'Date',          False, True,  40),
            ('agama',           'Agama',           'Identitas',  'individu', 'String (kode)', True,  True,  50),
            # Penerimaan
            ('laz_kode',        'LAZ',             'Penerimaan', 'individu', 'String',        True,  True,  60),
            ('program_kode',    'Program',         'Penerimaan', 'individu', 'String',        True,  True,  70),
            ('tipe_penerimaan', 'Tipe Penerimaan', 'Penerimaan', 'individu', 'String (kode)', True,  True,  80),
            ('tanggal_terima',  'Tanggal Terima',  'Penerimaan', 'individu', 'Date',          True,  True,  90),
            # Wilayah
            ('provinsi_kode',   'Provinsi',        'Wilayah',    'individu', 'String',        True,  True,  100),
            ('kabkota_kode',    'Kab/Kota',        'Wilayah',    'individu', 'String',        True,  True,  110),
            ('kecamatan_kode',  'Kecamatan',       'Wilayah',    'individu', 'String',        False, True,  120),
            ('kelurahan_kode',  'Kelurahan',       'Wilayah',    'individu', 'String',        False, True,  130),
        ]

        obj_map = {}
        for (fk, fl, fg, kat, ft, isf, isd, urt) in fields:
            obj = TampilanDtsen(
                field_key=fk, field_label=fl, field_group=fg,
                kategori=kat, field_type=ft,
                is_filter=int(isf), is_detail=int(isd),
                is_active=1, urutan=urt
            )
            db.session.add(obj)
            obj_map[fk] = obj

        db.session.flush()  # agar id terisi

        # ── Refs ────────────────────────────────────────────────────
        refs = {
            'jenis_kelamin': [
                ('m', 'Laki-laki', 1),
                ('f', 'Perempuan', 2),
            ],
            'agama': [
                ('Islam',    'Islam',    1),
                ('Kristen',  'Kristen',  2),
                ('Katolik',  'Katolik',  3),
                ('Hindu',    'Hindu',    4),
                ('Buddha',   'Buddha',   5),
                ('Konghucu', 'Konghucu', 6),
            ],
            'tipe_penerimaan': [
                ('pml',  'Langsung',       1),
                ('pmtl', 'Tidak Langsung', 2),
            ],
        }

        for field_key, items in refs.items():
            parent = obj_map.get(field_key)
            if not parent:
                continue
            for (rv, rl, urt) in items:
                db.session.add(TampilanDtsenRef(
                    tampilan_id=parent.id,
                    ref_value=rv, ref_label=rl, urutan=urt
                ))

        db.session.commit()
        print(f"[seed] Berhasil: {len(fields)} field, {sum(len(v) for v in refs.values())} refs.")


if __name__ == '__main__':
    run()
