from flask import request, jsonify
from . import api_v1_bp
from sqlalchemy import text
from ...extensions import db


@api_v1_bp.get("/lembaga")
def list_lembaga():
    skala = request.args.get("skala", type=int)
    bind = {}

    laz_where = """
        WHERE laz_status IN ('aktif','daftar_ulang')
        AND laz_nama IS NOT NULL
        AND TRIM(laz_nama) <> ''
    """

    uker_where = """
        WHERE is_kemenag = 0
        AND uker_nama IS NOT NULL
        AND TRIM(uker_nama) <> ''
    """

    # default jika skala tidak dikirim
    uker_skala = "NULL AS skala"

    if skala is not None:
        bind["skala"] = skala

        laz_where += """
            AND skala = :skala
        """

        uker_skala = ":skala AS skala"

        if skala == 1:
            uker_where += """
                AND uker_parent = 0
            """

        elif skala == 2:
            uker_where += """
                AND provinsi_kode IS NOT NULL
                AND kabkota_kode IS NULL
                AND kecamatan_kode IS NULL
            """

        elif skala == 3:
            uker_where += """
                AND provinsi_kode IS NOT NULL
                AND kabkota_kode IS NOT NULL
                AND kecamatan_kode IS NULL
            """

    sql = text(f"""
        SELECT
            laz_kode AS kode,
            UPPER(laz_nama) AS nama,
            skala,
            'laz' AS jenis
        FROM t_laz
        {laz_where}

        UNION ALL

        SELECT
            uker_kode AS kode,
            UPPER(singkatan) AS nama,
            {uker_skala},
            'kemenag' AS jenis
        FROM m_uker
        {uker_where}

        ORDER BY nama
    """)

    rows = db.session.execute(sql, bind).mappings().all()

    return jsonify([
        {
            "kode": row["kode"],
            "nama": row["nama"],
            "jenis": row["jenis"],
            "skala": row["skala"],
        }
        for row in rows
    ]), 200