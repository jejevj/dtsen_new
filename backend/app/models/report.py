from datetime import datetime
from ..extensions import db
from sqlalchemy import text


class Report:

    @staticmethod
    def get_param_tahun(params: dict) -> list:
        sql = text("""
        WITH RECURSIVE years AS (
            SELECT YEAR(CURDATE()) AS tahun
            UNION ALL
            SELECT tahun - 1
            FROM years
            WHERE tahun >= (SELECT DISTINCT YEAR(t_mustahik.tanggal_terima) FROM t_mustahik ORDER BY tanggal_terima ASC LIMIT 1)
        )
        SELECT tahun FROM years
        ORDER BY tahun DESC;
        """)

        rows = db.session.execute(sql).mappings().all()

        return [dict(row) for row in rows]
    
    @staticmethod
    def get_param_lembaga() -> list:
        sql = text("""
        SELECT laz_kode, laz_nama
        FROM t_laz
        WHERE laz_status IN ('aktif', 'daftar_ulang')
        AND skala > 0
        ORDER BY laz_nama;
        """)

        rows = db.session.execute(sql).mappings().all()

        return [dict(row) for row in rows]
    
    @staticmethod
    def get_skala_bzn() -> list:
        sql = text("""
        SELECT 1 skala, COUNT(uker_kode) bzn_count
        FROM m_uker
        WHERE uker_kode = 'BZN'
        GROUP BY uker_kode
        UNION
        SELECT 2 skala, COUNT(DISTINCT uker_kode) bzn_count
        FROM m_uker
        WHERE uker_parent = 'BZN'
        GROUP BY uker_parent
        UNION
        SELECT 3 skala, COUNT(DISTINCT uker_kode) bzn_count
        FROM m_uker
        WHERE kabkota_kode IS NOT NULL OR TRIM(kabkota_kode) != ''
        GROUP BY uker_parent;
        """)

        rows = db.session.execute(sql, {}).mappings().all()

        return [dict(row) for row in rows]
    
    @staticmethod
    def get_skala_laz() -> list:
        sql = text("""
        SELECT skala, laz_status, COUNT(laz_kode) laz_count
        FROM t_laz
        WHERE skala != 0
        GROUP BY skala, laz_status;
        """)

        rows = db.session.execute(sql, {}).mappings().all()

        return [dict(row) for row in rows]

    @staticmethod
    def get_desil_baseline() -> list:
        sql = text("""
        SELECT desil_nasional desil, SUM(jumlah_anggota_keluarga) nik_count 
        FROM (
        SELECT DISTINCT nomor_kartu_keluarga, desil_nasional, jumlah_anggota_keluarga FROM zawa_keluarga WHERE desil_nasional < 5
        )zawa
        GROUP BY desil_nasional;
        """)

        rows = db.session.execute(sql, {}).mappings().all()

        return [dict(row) for row in rows]

    @staticmethod
    def get_desil_mustahik(params: dict) -> list:
        tahun_awal = int(params.get("tahun") or datetime.now().year)
        tahun_akhir = int(params.get("tahun") or datetime.now().year) + 1
        
        sql_text = """
        SELECT t_mustahik_bappenas.desil, COUNT(DISTINCT t_mustahik_bappenas.nik) nik_count, SUM(t_mustahik.rupiah) rupiah
        FROM t_mustahik_bappenas
        LEFT JOIN t_mustahik ON t_mustahik.mustahik_id = t_mustahik_bappenas.mustahik_id
        WHERE t_mustahik_bappenas.desil BETWEEN 1 AND 4
        AND t_mustahik_bappenas.tahun_penyetaraan >= :start_date
        AND t_mustahik_bappenas.tahun_penyetaraan < :end_date
        """
        
        lembaga = params.get("lembaga") or None
        if lembaga:
            sql_text += "AND t_mustahik.laz_kode = :lembaga"

        sql_text += "GROUP BY t_mustahik_bappenas.desil;"
        
        sql = text(sql_text)

        rows = db.session.execute(sql, {
            'start_date': tahun_awal,
            'end_date': tahun_akhir,
            'lembaga': lembaga
        }).mappings().all()

        return [dict(row) for row in rows]
 
    @staticmethod
    def get_tren(params: dict) -> list:
        tahun = int(params.get("tahun") or datetime.now().year)

        sql_text = """
        WITH RECURSIVE years AS (
            SELECT :tahun AS tahun
            UNION ALL
            SELECT tahun - 1
            FROM years
            WHERE tahun > :tahun - 4
        )
        SELECT tahun"""

        lembaga = params.get("lembaga") or None
        if lembaga:
            sql_text += """
            , COALESCE((SELECT SUM(rupiah) FROM t_mustahik WHERE laz_kode = :lembaga AND tipe_penerimaan = 'pml' AND tanggal_terima >= CONCAT(tahun,'-01-01') AND tanggal_terima < CONCAT(tahun+1,'-01-01')), 0) AS Bantuan_Langsung
            , COALESCE((SELECT SUM(rupiah) FROM t_mustahik WHERE laz_kode = :lembaga AND tipe_penerimaan = 'pmtl' AND tanggal_terima >= CONCAT(tahun,'-01-01') AND tanggal_terima < CONCAT(tahun+1,'-01-01')), 0) AS Bantuan_Tidak_Langsung
            """
        else:
            sql_text += """
            , COALESCE((SELECT SUM(rupiah) FROM t_mustahik WHERE tipe_penerimaan = 'pml' AND tanggal_terima >= CONCAT(tahun,'-01-01') AND tanggal_terima < CONCAT(tahun+1,'-01-01')), 0) AS Bantuan_Langsung
            , COALESCE((SELECT SUM(rupiah) FROM t_mustahik WHERE tipe_penerimaan = 'pmtl' AND tanggal_terima >= CONCAT(tahun,'-01-01') AND tanggal_terima < CONCAT(tahun+1,'-01-01')), 0) AS Bantuan_Tidak_Langsung
            """
    
        sql_text += """
        FROM years
        ORDER BY tahun;
        """
        sql = text(sql_text)

        rows = db.session.execute(sql, {
            'tahun': tahun,
            'lembaga': lembaga
        }).mappings().all()

        return [dict(row) for row in rows]

    @staticmethod
    def get_gender(params: dict) -> list:
        tahun_awal = int(params.get("tahun") or datetime.now().year)
        tahun_akhir = int(params.get("tahun") or datetime.now().year) + 1

        sql_text = """
        SELECT jenis_kelamin, IFNULL(COUNT(DISTINCT nik), 0) mustahik
        FROM t_mustahik
        WHERE tanggal_terima >= :start_date
        AND tanggal_terima < :end_date
        """

        lembaga = params.get("lembaga") or None
        if lembaga:
            sql_text += "AND laz_kode = :lembaga"

        sql_text += """
        GROUP BY jenis_kelamin;
        """

        sql = text(sql_text)

        rows = db.session.execute(sql, {
            'start_date': f'{tahun_awal}-01-01',
            'end_date':   f'{tahun_akhir}-01-01',
            'lembaga': lembaga
        }).mappings().all()

        return [dict(row) for row in rows]

    @staticmethod
    def get_bidang(params: dict) -> list:
        tahun_awal = int(params.get("tahun") or datetime.now().year)
        tahun_akhir = int(params.get("tahun") or datetime.now().year) + 1

        sql_text = """
        SELECT
            b.bidang_kode,
            UPPER(b.bidang_label) AS bidang_label,
            COALESCE(x.total_penyaluran,0) AS total_penyaluran,
            COALESCE(x.total_mustahik,0) AS total_mustahik
        FROM m_bidang b
        LEFT JOIN (
            SELECT
                p.bidang_kode,
                SUM(m.rupiah) total_penyaluran,
                COUNT(DISTINCT m.nik) total_mustahik
            FROM t_program p
            JOIN t_mustahik m
                ON m.program_kode = p.program_kode
            WHERE m.tanggal_terima >= :start_date
            AND m.tanggal_terima < :end_date
        """

        lembaga = params.get("lembaga") or None
        if lembaga:
            sql_text += "AND m.laz_kode = :lembaga"

        sql_text += """
            GROUP BY p.bidang_kode
        ) x
        ON x.bidang_kode = b.bidang_kode
        ORDER BY b.is_prioritas DESC, b.bidang_kode;
        """

        sql = text(sql_text)

        rows = db.session.execute(sql, {
            'start_date': f'{tahun_awal}-01-01',
            'end_date':   f'{tahun_akhir}-01-01',
            'lembaga': lembaga
        }).mappings().all()

        return [dict(row) for row in rows]

    @staticmethod
    def get_map_provinsi(params: dict) -> list:
        tahun_awal = int(params.get("tahun") or datetime.now().year)
        tahun_akhir = int(params.get("tahun") or datetime.now().year) + 1
        
        sql = text("""
            SELECT t_mustahik.provinsi_kode, m_provinsi.provinsi_nama, SUM(rupiah) penyaluran, COUNT(DISTINCT nik) mustahik, COUNT(DISTINCT laz_kode) laz_count
            FROM t_mustahik
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
            WHERE t_mustahik.tanggal_terima >= :start_date
            AND t_mustahik.tanggal_terima < :end_date
            GROUP BY t_mustahik.provinsi_kode
            ORDER BY t_mustahik.provinsi_kode
        """)

        result = db.session.execute(sql, {
            'start_date': f'{tahun_awal}-01-01',
            'end_date':   f'{tahun_akhir}-01-01'
        }).mappings().all()

        return [dict(row) for row in result]
    
    @staticmethod
    def get_map_kabkota(params: dict) -> list:
        tahun_awal = int(params.get("tahun") or datetime.now().year)
        tahun_akhir = int(params.get("tahun") or datetime.now().year) + 1

        sql = text("""
            SELECT t_mustahik.provinsi_kode, t_mustahik.kabkota_kode, m_kabkota.kabkota_nama, SUM(rupiah) penyaluran, COUNT(DISTINCT nik) mustahik, COUNT(DISTINCT laz_kode) laz_count
            FROM t_mustahik
            JOIN m_kabkota ON m_kabkota.kabkota_kode = t_mustahik.kabkota_kode
            WHERE t_mustahik.tanggal_terima >= :start_date
            AND t_mustahik.tanggal_terima < :end_date
            GROUP BY t_mustahik.provinsi_kode, t_mustahik.kabkota_kode
            ORDER BY t_mustahik.provinsi_kode, t_mustahik.kabkota_kode
        """)

        result = db.session.execute(sql, {
            'start_date': f'{tahun_awal}-01-01',
            'end_date':   f'{tahun_akhir}-01-01'
        }).mappings().all()

        return [dict(row) for row in result]

    @staticmethod
    def get_map_kecamatan(params: dict) -> list:
        tahun_awal = int(params.get("tahun") or datetime.now().year)
        tahun_akhir = int(params.get("tahun") or datetime.now().year) + 1

        sql = text("""
            SELECT t_mustahik.provinsi_kode, t_mustahik.kabkota_kode, t_mustahik.kecamatan_kode, m_kecamatan.kecamatan_nama, SUM(rupiah) penyaluran, COUNT(DISTINCT nik) mustahik, COUNT(DISTINCT laz_kode) laz_count
            FROM t_mustahik
            JOIN m_kecamatan ON m_kecamatan.kecamatan_kode = t_mustahik.kecamatan_kode
            WHERE t_mustahik.tanggal_terima >= :start_date
            AND t_mustahik.tanggal_terima < :end_date
            GROUP BY t_mustahik.provinsi_kode, t_mustahik.kabkota_kode, t_mustahik.kecamatan_kode
            ORDER BY t_mustahik.provinsi_kode, t_mustahik.kabkota_kode, t_mustahik.kecamatan_kode
        """)

        result = db.session.execute(sql, {
            'start_date': f'{tahun_awal}-01-01',
            'end_date':   f'{tahun_akhir}-01-01'
        }).mappings().all()

        return [dict(row) for row in result]

# ==============================================================================================================================  
# DASHBOARD 
# ==============================================================================================================================
    @staticmethod
    def get_param_laz(params: dict) -> list:
        email = (params.get("email") or '')
        sql = text("""
        SELECT DISTINCT t_laz.laz_kode kode, t_laz.laz_nama nama
        FROM t_laz
        WHERE t_laz.skala != 0
        AND t_laz.laz_kode = COALESCE((SELECT t_dtsen_akses.laz_kode FROM t_dtsen_akses WHERE email = :email), t_laz.laz_kode);
        """)

        result = db.session.execute(sql, {
            'email': email
        }).mappings().all()

        return [dict(row) for row in result]
    
    @staticmethod
    def get_param_provinsi(params: dict) -> list:
        email = (params.get("email") or '')

        sql = text("""
            SELECT t_dtsen_wilayah.provinsi_kode kode, m_provinsi.provinsi_nama nama
            FROM t_dtsen_akses
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.dtsen_akses_id = t_dtsen_akses.dtsen_akses_id
            JOIN t_laz ON t_laz.laz_kode = t_dtsen_akses.laz_kode
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_dtsen_wilayah.provinsi_kode
            WHERE t_dtsen_akses.email = :email
            AND t_dtsen_akses.statuses = 'aktif'
            UNION
            SELECT t_laz.provinsi_kode kode, m_provinsi.provinsi_nama nama
            FROM t_dtsen_akses
            JOIN t_laz ON t_laz.laz_kode = t_dtsen_akses.laz_kode
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_laz.provinsi_kode
            WHERE t_dtsen_akses.email = :email
            AND t_dtsen_akses.statuses = 'aktif'
            ORDER BY kode;
        """)

        result = db.session.execute(sql, {
            'email': email
        }).mappings().all()

        return [dict(row) for row in result]
    
    @staticmethod
    def get_param_kabkota(params: dict) -> list:
        email = (params.get("email") or '')
        provinsi_kode = (params.get("provinsi_kode") or None)

        sql = text("""
            SELECT m_kabkota.kabkota_kode kode, m_kabkota.kabkota_nama nama
            FROM m_kabkota
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_kabkota.provinsi_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
            WHERE (t_dtsen_wilayah.kabkota_kode = m_kabkota.kabkota_kode OR t_dtsen_wilayah.kabkota_kode IS NULL)
            AND (t_dtsen_wilayah.provinsi_kode = :provinsi_kode OR t_dtsen_wilayah.provinsi_kode IS NULL)
            AND t_dtsen_akses.email = :email
            ORDER BY kode;
        """)

        result = db.session.execute(sql, {
            'provinsi_kode': provinsi_kode,
            'email': email
        }).mappings().all()

        return [dict(row) for row in result]
 
    @staticmethod
    def get_param_kecamatan(params: dict) -> list:
        email = (params.get("email") or '')
        kabkota_kode = (params.get("kabkota_kode") or None)

        sql_text = """
        SELECT m_kecamatan.kecamatan_kode kode, m_kecamatan.kecamatan_nama nama
        FROM m_kecamatan
        LEFT JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = LEFT(m_kecamatan.kabkota_kode,2)
        JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
        WHERE (t_dtsen_wilayah.kecamatan_kode = m_kecamatan.kecamatan_kode OR t_dtsen_wilayah.kecamatan_kode IS NULL)
        AND t_dtsen_akses.email = :email
        """

        kabkota_kode = params.get("kabkota_kode") or None
        if kabkota_kode:
            sql_text += "AND m_kecamatan.kabkota_kode = :kabkota_kode"

        sql_text += """
        ORDER BY kode;
        """

        sql = text(sql_text)

        result = db.session.execute(sql, {
            'email': email,
            'kabkota_kode': kabkota_kode
        }).mappings().all()

        return [dict(row) for row in result]
    
    @staticmethod
    def get_data_bidang(params: dict) -> list:
        tahun_awal = int(params.get("tahun") or datetime.now().year)
        tahun_akhir = int(params.get("tahun") or datetime.now().year) + 1
        email = (params.get("email") or '')
        provinsi_kode = (params.get("provinsi_kode") or None)
        kabkota_kode = (params.get("kabkota_kode") or None)
        kacamatan_kode = (params.get("kacamatan_kode") or None)

        sql_level = 1
        sql_param_data = "ktp_provinsi_kode"
        sql_where = ""

        if provinsi_kode:
            sql_level = 2
            sql_param_data = "ktp_kabkota_kode"
            sql_where = " AND provinsi_kode = :provinsi_kode"

        if kabkota_kode:
            sql_level = 3
            sql_param_data = "ktp_kecamatan_kode"
            sql_where = " AND kabkota_kode = :kabkota_kode"

        if kacamatan_kode:
            sql_level = 3
            sql_param_data = "ktp_kecamatan_kode"
            sql_where = " AND kacamatan_kode = :kacamatan_kode"

        sql_text = """
        SELECT DISTINCT *
        
        FROM
        (
            SELECT m_provinsi.provinsi_kode zawa, m_provinsi.provinsi_kode kode, m_provinsi.provinsi_nama nama, t_dtsen_akses.laz_kode laz, 1 lvl,
            m_provinsi.provinsi_nama lvl_1, '-' lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, null kabkota_kode, null kacamatan_kode
            FROM m_provinsi
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_provinsi.provinsi_kode OR t_dtsen_wilayah.provinsi_kode IS NULL
            JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
            WHERE t_dtsen_akses.email = :email
            AND provinsi_aktif = 'y'
            UNION
            SELECT CONCAT(SUBSTRING(m_kabkota.kabkota_kode, 1, 2), '.', SUBSTRING(m_kabkota.kabkota_kode, 3, 2)) zawa, 
            m_kabkota.kabkota_kode kode, m_kabkota.kabkota_nama nama, t_dtsen_akses.laz_kode laz, 2 lvl,
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, null kacamatan_kode
            FROM m_kabkota
            JOIN m_provinsi ON m_provinsi.provinsi_kode = m_kabkota.provinsi_kode 
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_kabkota.provinsi_kode 
            AND (t_dtsen_wilayah.kabkota_kode = m_kabkota.kabkota_kode OR t_dtsen_wilayah.kabkota_kode IS NULL)
            JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
            WHERE t_dtsen_akses.email = :email
            AND kabkota_aktif = 'y'
            UNION
            SELECT CONCAT(SUBSTRING(m_kecamatan.kecamatan_kode, 1, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 3, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 5, 2)) zawa, 
            m_kecamatan.kecamatan_kode kode, m_kecamatan.kecamatan_nama nama, t_dtsen_akses.laz_kode laz, 3 lvl,
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, m_kecamatan.kecamatan_nama lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, m_kecamatan.kecamatan_kode
            FROM m_kecamatan
            JOIN m_kabkota ON m_kabkota.kabkota_kode = m_kecamatan.kabkota_kode
            JOIN m_provinsi ON m_provinsi.provinsi_kode = m_kabkota.provinsi_kode
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_kabkota.provinsi_kode 
            AND (t_dtsen_wilayah.kabkota_kode = m_kabkota.kabkota_kode OR t_dtsen_wilayah.kabkota_kode IS NULL)
            AND (t_dtsen_wilayah.kecamatan_kode = m_kecamatan.kecamatan_kode OR t_dtsen_wilayah.kecamatan_kode IS NULL)
            JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
            WHERE t_dtsen_akses.email = :email
            AND kecamatan_aktif = 'y'
            UNION
            SELECT DISTINCT t_mustahik.provinsi_kode zawa, t_mustahik.provinsi_kode kode, m_provinsi.provinsi_nama nama, t_dtsen_akses.laz_kode laz, 1 lvl,
            m_provinsi.provinsi_nama lvl_1, '-' lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, null kabkota_kode, null kacamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
            UNION
            SELECT DISTINCT CONCAT(SUBSTRING(m_kabkota.kabkota_kode, 1, 2), '.', SUBSTRING(m_kabkota.kabkota_kode, 3, 2)) zawa, 
            m_kabkota.kabkota_kode kode, m_kabkota.kabkota_nama nama, t_dtsen_akses.laz_kode laz, 2 lvl,
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, null kacamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
            JOIN m_kabkota ON m_kabkota.provinsi_kode = m_provinsi.provinsi_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
            UNION
            SELECT DISTINCT CONCAT(SUBSTRING(m_kecamatan.kecamatan_kode, 1, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 3, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 5, 2)) zawa, 
            m_kecamatan.kecamatan_kode kode, m_kecamatan.kecamatan_nama nama, t_dtsen_akses.laz_kode laz, 3 lvl, 
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, m_kecamatan.kecamatan_nama lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, m_kecamatan.kecamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
            JOIN m_kabkota ON m_kabkota.provinsi_kode = m_provinsi.provinsi_kode
            JOIN m_kecamatan ON m_kecamatan.kabkota_kode = m_kabkota.kabkota_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
        ) wilayah
        WHERE wilayah.lvl = :sql_level
        """

        sql = text(sql_text + sql_where)

        result = db.session.execute(sql, {
            'tahun_awal'    : f'{tahun_awal}-01-01',
            'tahun_akhir'   : f'{tahun_akhir}-01-01',
            'email'         : email,
            'sql_level'     : sql_level,
            'provinsi_kode' : provinsi_kode,
            'kabkota_kode'  : kabkota_kode,
            'kacamatan_kode': kacamatan_kode
        }).mappings().all()

        return [dict(row) for row in result]

    @staticmethod
    def get_baseline_wilayah(params: dict) -> list:
        tahun_awal = int(params.get("tahun") or datetime.now().year)
        tahun_akhir = int(params.get("tahun") or datetime.now().year) + 1
        email = (params.get("email") or '')
        provinsi_kode = (params.get("provinsi_kode") or None)
        kabkota_kode = (params.get("kabkota_kode") or None)
        kacamatan_kode = (params.get("kacamatan_kode") or None)

        sql_level = 1
        sql_param_base = "kode_provinsi"
        sql_where = ""

        if provinsi_kode:
            sql_level = 2
            sql_param_base = "kode_kabupaten_kota"
            sql_where = " AND provinsi_kode = :provinsi_kode"

        if kabkota_kode:
            sql_level = 3
            sql_param_base = "kode_kecamatan"
            sql_where = " AND kabkota_kode = :kabkota_kode"

        if kacamatan_kode:
            sql_level = 3
            sql_param_base = "kode_kecamatan"
            sql_where = " AND kacamatan_kode = :kacamatan_kode"

        sql_text = """
        SELECT DISTINCT wilayah.lvl, wilayah.zawa, wilayah.kode, wilayah.nama, wilayah.lvl_1, wilayah.lvl_2, wilayah.lvl_3
        , COALESCE((SELECT SUM(jumlah_anggota_keluarga) FROM zawa_keluarga WHERE desil_nasional < 5 AND 
        """ + sql_param_base + """ 
        COLLATE utf8mb4_unicode_ci = wilayah.zawa COLLATE utf8mb4_unicode_ci),0) baseline
        , 0 mustahik, 0 rupiah
        FROM
        (
        SELECT m_provinsi.provinsi_kode zawa, m_provinsi.provinsi_kode kode, m_provinsi.provinsi_nama nama, 1 lvl, t_dtsen_akses.laz_kode laz,
        m_provinsi.provinsi_nama lvl_1, '-' lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, null kabkota_kode, null kacamatan_kode
        FROM m_provinsi
        JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_provinsi.provinsi_kode OR t_dtsen_wilayah.provinsi_kode IS NULL
        JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
        WHERE t_dtsen_akses.email = :email
        AND provinsi_aktif = 'y'
        UNION
        SELECT CONCAT(SUBSTRING(m_kabkota.kabkota_kode, 1, 2), '.', SUBSTRING(m_kabkota.kabkota_kode, 3, 2)) zawa, 
        m_kabkota.kabkota_kode kode, m_kabkota.kabkota_nama nama, 2 lvl, t_dtsen_akses.laz_kode laz,
        m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, null kacamatan_kode
        FROM m_kabkota
        JOIN m_provinsi ON m_provinsi.provinsi_kode = m_kabkota.provinsi_kode 
        JOIN t_dtsen_wilayah ON (t_dtsen_wilayah.provinsi_kode = m_kabkota.provinsi_kode OR t_dtsen_wilayah.provinsi_kode IS NULL)
        AND (t_dtsen_wilayah.kabkota_kode = m_kabkota.kabkota_kode OR t_dtsen_wilayah.kabkota_kode IS NULL)
        JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
        WHERE t_dtsen_akses.email = :email
        AND kabkota_aktif = 'y'
        UNION
        SELECT CONCAT(SUBSTRING(m_kecamatan.kecamatan_kode, 1, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 3, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 5, 2)) zawa, 
        m_kecamatan.kecamatan_kode kode, m_kecamatan.kecamatan_nama nama, 3 lvl, t_dtsen_akses.laz_kode laz,
        m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, m_kecamatan.kecamatan_nama lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, m_kecamatan.kecamatan_kode
        FROM m_kecamatan
        JOIN m_kabkota ON m_kabkota.kabkota_kode = m_kecamatan.kabkota_kode
        JOIN m_provinsi ON m_provinsi.provinsi_kode = m_kabkota.provinsi_kode
        JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_kabkota.provinsi_kode 
        AND (t_dtsen_wilayah.kabkota_kode = m_kabkota.kabkota_kode OR t_dtsen_wilayah.kabkota_kode IS NULL)
        AND (t_dtsen_wilayah.kecamatan_kode = m_kecamatan.kecamatan_kode OR t_dtsen_wilayah.kecamatan_kode IS NULL)
        JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
        WHERE t_dtsen_akses.email = :email
        AND kecamatan_aktif = 'y'
        ) wilayah
        WHERE wilayah.lvl = :sql_level
        """

        sql = text(sql_text + sql_where)

        result = db.session.execute(sql, {
            'tahun_awal'    : f'{tahun_awal}-01-01',
            'tahun_akhir'   : f'{tahun_akhir}-01-01',
            'email'         : email,
            'sql_level'     : sql_level,
            'provinsi_kode' : provinsi_kode,
            'kabkota_kode'  : kabkota_kode,
            'kacamatan_kode': kacamatan_kode
        }).mappings().all()

        return [dict(row) for row in result]
    
    @staticmethod
    def get_data_wilayah(params: dict) -> list:
        tahun_awal = int(params.get("tahun") or datetime.now().year)
        tahun_akhir = int(params.get("tahun") or datetime.now().year) + 1
        email = (params.get("email") or '')
        provinsi_kode = (params.get("provinsi_kode") or None)
        kabkota_kode = (params.get("kabkota_kode") or None)
        kacamatan_kode = (params.get("kacamatan_kode") or None)

        sql_level = 1
        sql_param_data = "ktp_provinsi_kode"
        sql_where = ""

        if provinsi_kode:
            sql_level = 2
            sql_param_data = "ktp_kabkota_kode"
            sql_where = " AND provinsi_kode = :provinsi_kode"

        if kabkota_kode:
            sql_level = 3
            sql_param_data = "ktp_kecamatan_kode"
            sql_where = " AND kabkota_kode = :kabkota_kode"

        if kacamatan_kode:
            sql_level = 3
            sql_param_data = "ktp_kecamatan_kode"
            sql_where = " AND kacamatan_kode = :kacamatan_kode"

        sql_text = """
        SELECT DISTINCT wilayah.lvl, wilayah.zawa, wilayah.kode, wilayah.nama, wilayah.lvl_1, wilayah.lvl_2, wilayah.lvl_3
        , 0 baseline
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil < 5 
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) mustahik
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik.jenis_kelamin = 'M' 
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) mustahik_m
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik.jenis_kelamin = 'F' 
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) mustahik_f
        , COALESCE((
            SELECT SUM(t_mustahik.rupiah) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil < 5 
            AND t_mustahik.tanggal_terima >= :tahun_awal
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ),0) rupiah
        , COALESCE((
            SELECT SUM(t_mustahik.rupiah) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik.tanggal_terima >= :tahun_awal
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ),0) rupiah_all
        FROM
        (
            SELECT m_provinsi.provinsi_kode zawa, m_provinsi.provinsi_kode kode, m_provinsi.provinsi_nama nama, t_dtsen_akses.laz_kode laz, 1 lvl,
            m_provinsi.provinsi_nama lvl_1, '-' lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, null kabkota_kode, null kacamatan_kode
            FROM m_provinsi
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_provinsi.provinsi_kode OR t_dtsen_wilayah.provinsi_kode IS NULL
            JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
            WHERE t_dtsen_akses.email = :email
            AND provinsi_aktif = 'y'
            UNION
            SELECT CONCAT(SUBSTRING(m_kabkota.kabkota_kode, 1, 2), '.', SUBSTRING(m_kabkota.kabkota_kode, 3, 2)) zawa, 
            m_kabkota.kabkota_kode kode, m_kabkota.kabkota_nama nama, t_dtsen_akses.laz_kode laz, 2 lvl,
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, null kacamatan_kode
            FROM m_kabkota
            JOIN m_provinsi ON m_provinsi.provinsi_kode = m_kabkota.provinsi_kode 
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_kabkota.provinsi_kode 
            AND (t_dtsen_wilayah.kabkota_kode = m_kabkota.kabkota_kode OR t_dtsen_wilayah.kabkota_kode IS NULL)
            JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
            WHERE t_dtsen_akses.email = :email
            AND kabkota_aktif = 'y'
            UNION
            SELECT CONCAT(SUBSTRING(m_kecamatan.kecamatan_kode, 1, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 3, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 5, 2)) zawa, 
            m_kecamatan.kecamatan_kode kode, m_kecamatan.kecamatan_nama nama, t_dtsen_akses.laz_kode laz, 3 lvl,
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, m_kecamatan.kecamatan_nama lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, m_kecamatan.kecamatan_kode
            FROM m_kecamatan
            JOIN m_kabkota ON m_kabkota.kabkota_kode = m_kecamatan.kabkota_kode
            JOIN m_provinsi ON m_provinsi.provinsi_kode = m_kabkota.provinsi_kode
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_kabkota.provinsi_kode 
            AND (t_dtsen_wilayah.kabkota_kode = m_kabkota.kabkota_kode OR t_dtsen_wilayah.kabkota_kode IS NULL)
            AND (t_dtsen_wilayah.kecamatan_kode = m_kecamatan.kecamatan_kode OR t_dtsen_wilayah.kecamatan_kode IS NULL)
            JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
            WHERE t_dtsen_akses.email = :email
            AND kecamatan_aktif = 'y'
            UNION
            SELECT DISTINCT t_mustahik.provinsi_kode zawa, t_mustahik.provinsi_kode kode, m_provinsi.provinsi_nama nama, t_dtsen_akses.laz_kode laz, 1 lvl,
            m_provinsi.provinsi_nama lvl_1, '-' lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, null kabkota_kode, null kacamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
            UNION
            SELECT DISTINCT CONCAT(SUBSTRING(m_kabkota.kabkota_kode, 1, 2), '.', SUBSTRING(m_kabkota.kabkota_kode, 3, 2)) zawa, 
            m_kabkota.kabkota_kode kode, m_kabkota.kabkota_nama nama, t_dtsen_akses.laz_kode laz, 2 lvl,
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, null kacamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
            JOIN m_kabkota ON m_kabkota.provinsi_kode = m_provinsi.provinsi_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
            UNION
            SELECT DISTINCT CONCAT(SUBSTRING(m_kecamatan.kecamatan_kode, 1, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 3, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 5, 2)) zawa, 
            m_kecamatan.kecamatan_kode kode, m_kecamatan.kecamatan_nama nama, t_dtsen_akses.laz_kode laz, 3 lvl, 
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, m_kecamatan.kecamatan_nama lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, m_kecamatan.kecamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
            JOIN m_kabkota ON m_kabkota.provinsi_kode = m_provinsi.provinsi_kode
            JOIN m_kecamatan ON m_kecamatan.kabkota_kode = m_kabkota.kabkota_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
        ) wilayah
        WHERE wilayah.lvl = :sql_level
        """

        sql = text(sql_text + sql_where)

        result = db.session.execute(sql, {
            'tahun_awal'    : f'{tahun_awal}-01-01',
            'tahun_akhir'   : f'{tahun_akhir}-01-01',
            'email'         : email,
            'sql_level'     : sql_level,
            'provinsi_kode' : provinsi_kode,
            'kabkota_kode'  : kabkota_kode,
            'kacamatan_kode': kacamatan_kode
        }).mappings().all()

        return [dict(row) for row in result]
    
    @staticmethod
    def get_baseline_desil(params: dict) -> list:
        tahun_awal = int(params.get("tahun") or datetime.now().year)
        tahun_akhir = int(params.get("tahun") or datetime.now().year) + 1
        email = (params.get("email") or '')
        provinsi_kode = (params.get("provinsi_kode") or None)
        kabkota_kode = (params.get("kabkota_kode") or None)
        kacamatan_kode = (params.get("kacamatan_kode") or None)

        sql_level = 1
        sql_param_base = "kode_provinsi"
        sql_where = ""

        if provinsi_kode:
            sql_level = 2
            sql_param_base = "kode_kabupaten_kota"
            sql_where = " AND provinsi_kode = :provinsi_kode"

        if kabkota_kode:
            sql_level = 3
            sql_param_base = "kode_kecamatan"
            sql_where = " AND kabkota_kode = :kabkota_kode"

        if kacamatan_kode:
            sql_level = 3
            sql_param_base = "kode_kecamatan"
            sql_where = " AND kacamatan_kode = :kacamatan_kode"

        sql_text = """
        SELECT DISTINCT wilayah.lvl, wilayah.zawa, wilayah.kode, wilayah.nama, wilayah.lvl_1, wilayah.lvl_2, wilayah.lvl_3
        , COALESCE((SELECT SUM(jumlah_anggota_keluarga) FROM zawa_keluarga WHERE desil_nasional = 1 AND 
        """ + sql_param_base + """ 
        COLLATE utf8mb4_unicode_ci = wilayah.zawa COLLATE utf8mb4_unicode_ci),0) desil_1
        , COALESCE((SELECT SUM(jumlah_anggota_keluarga) FROM zawa_keluarga WHERE desil_nasional = 2 AND 
        """ + sql_param_base + """ 
        COLLATE utf8mb4_unicode_ci = wilayah.zawa COLLATE utf8mb4_unicode_ci),0) desil_2
        , COALESCE((SELECT SUM(jumlah_anggota_keluarga) FROM zawa_keluarga WHERE desil_nasional = 3 AND 
        """ + sql_param_base + """ 
        COLLATE utf8mb4_unicode_ci = wilayah.zawa COLLATE utf8mb4_unicode_ci),0) desil_3
        , COALESCE((SELECT SUM(jumlah_anggota_keluarga) FROM zawa_keluarga WHERE desil_nasional = 4 AND 
        """ + sql_param_base + """ 
        COLLATE utf8mb4_unicode_ci = wilayah.zawa COLLATE utf8mb4_unicode_ci),0) desil_4
        FROM
        (
        SELECT m_provinsi.provinsi_kode zawa, m_provinsi.provinsi_kode kode, m_provinsi.provinsi_nama nama, 1 lvl, t_dtsen_akses.laz_kode laz,
        m_provinsi.provinsi_nama lvl_1, '-' lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, null kabkota_kode, null kacamatan_kode
        FROM m_provinsi
        JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_provinsi.provinsi_kode OR t_dtsen_wilayah.provinsi_kode IS NULL
        JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
        WHERE t_dtsen_akses.email = :email
        AND provinsi_aktif = 'y'
        UNION
        SELECT CONCAT(SUBSTRING(m_kabkota.kabkota_kode, 1, 2), '.', SUBSTRING(m_kabkota.kabkota_kode, 3, 2)) zawa, 
        m_kabkota.kabkota_kode kode, m_kabkota.kabkota_nama nama, 2 lvl, t_dtsen_akses.laz_kode laz,
        m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, null kacamatan_kode
        FROM m_kabkota
        JOIN m_provinsi ON m_provinsi.provinsi_kode = m_kabkota.provinsi_kode 
        JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_kabkota.provinsi_kode 
        AND (t_dtsen_wilayah.kabkota_kode = m_kabkota.kabkota_kode OR t_dtsen_wilayah.kabkota_kode IS NULL)
        JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
        WHERE t_dtsen_akses.email = :email
        AND kabkota_aktif = 'y'
        UNION
        SELECT CONCAT(SUBSTRING(m_kecamatan.kecamatan_kode, 1, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 3, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 5, 2)) zawa, 
        m_kecamatan.kecamatan_kode kode, m_kecamatan.kecamatan_nama nama, 3 lvl, t_dtsen_akses.laz_kode laz,
        m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, m_kecamatan.kecamatan_nama lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, m_kecamatan.kecamatan_kode
        FROM m_kecamatan
        JOIN m_kabkota ON m_kabkota.kabkota_kode = m_kecamatan.kabkota_kode
        JOIN m_provinsi ON m_provinsi.provinsi_kode = m_kabkota.provinsi_kode
        JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_kabkota.provinsi_kode 
        AND (t_dtsen_wilayah.kabkota_kode = m_kabkota.kabkota_kode OR t_dtsen_wilayah.kabkota_kode IS NULL)
        AND (t_dtsen_wilayah.kecamatan_kode = m_kecamatan.kecamatan_kode OR t_dtsen_wilayah.kecamatan_kode IS NULL)
        JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
        WHERE t_dtsen_akses.email = :email
        AND kecamatan_aktif = 'y'
        ) wilayah
        WHERE wilayah.lvl = :sql_level
        """

        sql = text(sql_text + sql_where)

        result = db.session.execute(sql, {
            'tahun_awal'    : f'{tahun_awal}-01-01',
            'tahun_akhir'   : f'{tahun_akhir}-01-01',
            'email'         : email,
            'sql_level'     : sql_level,
            'provinsi_kode' : provinsi_kode,
            'kabkota_kode'  : kabkota_kode,
            'kacamatan_kode': kacamatan_kode
        }).mappings().all()

        return [dict(row) for row in result]
    
    @staticmethod
    def get_data_desil(params: dict) -> list:
        tahun_awal = int(params.get("tahun") or datetime.now().year)
        tahun_akhir = int(params.get("tahun") or datetime.now().year) + 1
        email = (params.get("email") or '')
        provinsi_kode = (params.get("provinsi_kode") or None)
        kabkota_kode = (params.get("kabkota_kode") or None)
        kacamatan_kode = (params.get("kacamatan_kode") or None)

        sql_level = 1
        sql_param_data = "ktp_provinsi_kode"
        sql_param_zawa = "kode_provinsi_ktp"
        sql_where = ""

        if provinsi_kode:
            sql_level = 2
            sql_param_data = "ktp_kabkota_kode"
            sql_param_zawa = "kode_kabupaten_kota_ktp"
            sql_where = " AND provinsi_kode = :provinsi_kode"

        if kabkota_kode:
            sql_level = 3
            sql_param_data = "ktp_kecamatan_kode"
            sql_param_zawa = "kode_kecamatan_ktp"
            sql_where = " AND kabkota_kode = :kabkota_kode"

        if kacamatan_kode:
            sql_level = 3
            sql_param_data = "ktp_kecamatan_kode"
            sql_param_zawa = "kode_kecamatan_ktp"
            sql_where = " AND kacamatan_kode = :kacamatan_kode"

        sql_text = """
        SELECT DISTINCT wilayah.lvl, wilayah.zawa, wilayah.kode, wilayah.nama, wilayah.lvl_1, wilayah.lvl_2, wilayah.lvl_3
        , 0 baseline
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil NOT IN (1,2,3,4,5,6,7,8,9,10) 
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) desil_na
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil = 1
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) desil_1
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil = 2
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) desil_2
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil = 3
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) desil_3
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil = 4
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) desil_4
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil = 5
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) desil_5
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil = 6
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) desil_6
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil = 7
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) desil_7
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil = 8
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) desil_8
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil = 9
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) desil_9
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil = 10
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) desil_10
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) desil_all
        , COALESCE((
            SELECT SUM(t_mustahik.rupiah) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik.tanggal_terima >= :tahun_awal
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ),0) desil_sum_all
        , COALESCE((
            SELECT SUM(t_mustahik.rupiah) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil NOT IN (1,2,3,4)
            AND t_mustahik.tanggal_terima >= :tahun_awal
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ),0) desil_sum_na
        , COALESCE((
            SELECT SUM(t_mustahik.rupiah) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil = 1
            AND t_mustahik.tanggal_terima >= :tahun_awal
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ),0) desil_sum_1
        , COALESCE((
            SELECT SUM(t_mustahik.rupiah) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil = 2
            AND t_mustahik.tanggal_terima >= :tahun_awal
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ),0) desil_sum_2
        , COALESCE((
            SELECT SUM(t_mustahik.rupiah) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil = 3
            AND t_mustahik.tanggal_terima >= :tahun_awal
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ),0) desil_sum_3
        , COALESCE((
            SELECT SUM(t_mustahik.rupiah) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik_bappenas.desil = 4
            AND t_mustahik.tanggal_terima >= :tahun_awal
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ),0) desil_sum_4
        FROM
        (
            SELECT m_provinsi.provinsi_kode zawa, m_provinsi.provinsi_kode kode, m_provinsi.provinsi_nama nama, t_dtsen_akses.laz_kode laz, 1 lvl,
            m_provinsi.provinsi_nama lvl_1, '-' lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, null kabkota_kode, null kacamatan_kode 
            FROM m_provinsi
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_provinsi.provinsi_kode OR t_dtsen_wilayah.provinsi_kode IS NULL
            JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
            WHERE t_dtsen_akses.email = :email
            AND provinsi_aktif = 'y'
            UNION
            SELECT CONCAT(SUBSTRING(m_kabkota.kabkota_kode, 1, 2), '.', SUBSTRING(m_kabkota.kabkota_kode, 3, 2)) zawa, 
            m_kabkota.kabkota_kode kode, m_kabkota.kabkota_nama nama, t_dtsen_akses.laz_kode laz, 2 lvl,
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, null kacamatan_kode
            FROM m_kabkota
            JOIN m_provinsi ON m_provinsi.provinsi_kode = m_kabkota.provinsi_kode 
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_kabkota.provinsi_kode 
            AND (t_dtsen_wilayah.kabkota_kode = m_kabkota.kabkota_kode OR t_dtsen_wilayah.kabkota_kode IS NULL)
            JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
            WHERE t_dtsen_akses.email = :email
            AND kabkota_aktif = 'y'
            UNION
            SELECT CONCAT(SUBSTRING(m_kecamatan.kecamatan_kode, 1, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 3, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 5, 2)) zawa, 
            m_kecamatan.kecamatan_kode kode, m_kecamatan.kecamatan_nama nama, t_dtsen_akses.laz_kode laz, 3 lvl,
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, m_kecamatan.kecamatan_nama lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, m_kecamatan.kecamatan_kode
            FROM m_kecamatan
            JOIN m_kabkota ON m_kabkota.kabkota_kode = m_kecamatan.kabkota_kode
            JOIN m_provinsi ON m_provinsi.provinsi_kode = m_kabkota.provinsi_kode
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_kabkota.provinsi_kode 
            AND (t_dtsen_wilayah.kabkota_kode = m_kabkota.kabkota_kode OR t_dtsen_wilayah.kabkota_kode IS NULL)
            AND (t_dtsen_wilayah.kecamatan_kode = m_kecamatan.kecamatan_kode OR t_dtsen_wilayah.kecamatan_kode IS NULL)
            JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
            WHERE t_dtsen_akses.email = :email
            AND kecamatan_aktif = 'y'
            UNION
            SELECT DISTINCT t_mustahik.provinsi_kode zawa, t_mustahik.provinsi_kode kode, m_provinsi.provinsi_nama nama, t_dtsen_akses.laz_kode laz, 1 lvl,
            m_provinsi.provinsi_nama lvl_1, '-' lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, null kabkota_kode, null kacamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
            UNION
            SELECT DISTINCT CONCAT(SUBSTRING(m_kabkota.kabkota_kode, 1, 2), '.', SUBSTRING(m_kabkota.kabkota_kode, 3, 2)) zawa, 
            m_kabkota.kabkota_kode kode, m_kabkota.kabkota_nama nama, t_dtsen_akses.laz_kode laz, 2 lvl,
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, null kacamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
            JOIN m_kabkota ON m_kabkota.provinsi_kode = m_provinsi.provinsi_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
            UNION
            SELECT DISTINCT CONCAT(SUBSTRING(m_kecamatan.kecamatan_kode, 1, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 3, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 5, 2)) zawa, 
            m_kecamatan.kecamatan_kode kode, m_kecamatan.kecamatan_nama nama, t_dtsen_akses.laz_kode laz, 3 lvl, 
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, m_kecamatan.kecamatan_nama lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, m_kecamatan.kecamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
            JOIN m_kabkota ON m_kabkota.provinsi_kode = m_provinsi.provinsi_kode
            JOIN m_kecamatan ON m_kecamatan.kabkota_kode = m_kabkota.kabkota_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
        ) wilayah
        WHERE wilayah.lvl = :sql_level
        """

        sql = text(sql_text + sql_where)

        result = db.session.execute(sql, {
            'tahun_awal'    : f'{tahun_awal}-01-01',
            'tahun_akhir'   : f'{tahun_akhir}-01-01',
            'email'         : email,
            'sql_level'     : sql_level,
            'provinsi_kode' : provinsi_kode,
            'kabkota_kode'  : kabkota_kode,
            'kacamatan_kode': kacamatan_kode
        }).mappings().all()

        return [dict(row) for row in result]
    
    @staticmethod
    def get_data_usia(params: dict) -> list:
        tahun_awal = int(params.get("tahun") or datetime.now().year)
        tahun_akhir = int(params.get("tahun") or datetime.now().year) + 1
        email = (params.get("email") or '')
        provinsi_kode = (params.get("provinsi_kode") or None)
        kabkota_kode = (params.get("kabkota_kode") or None)
        kacamatan_kode = (params.get("kacamatan_kode") or None)

        tahun_lahir_1 = datetime.now().year - 10
        tahun_lahir_2 = tahun_lahir_1 - 10
        tahun_lahir_3 = tahun_lahir_2 - 10
        tahun_lahir_4 = tahun_lahir_3 - 10
        tahun_lahir_5 = tahun_lahir_4 - 10
        tahun_lahir_6 = tahun_lahir_5 - 10

        sql_level = 1
        sql_param_data = "ktp_provinsi_kode"
        sql_param_zawa = "kode_provinsi_ktp"
        sql_where = ""

        if provinsi_kode:
            sql_level = 2
            sql_param_data = "ktp_kabkota_kode"
            sql_param_zawa = "kode_kabupaten_kota_ktp"
            sql_where = " AND provinsi_kode = :provinsi_kode"

        if kabkota_kode:
            sql_level = 3
            sql_param_data = "ktp_kecamatan_kode"
            sql_param_zawa = "kode_kecamatan_ktp"
            sql_where = " AND kabkota_kode = :kabkota_kode"

        if kacamatan_kode:
            sql_level = 3
            sql_param_data = "ktp_kecamatan_kode"
            sql_param_zawa = "kode_kecamatan_ktp"
            sql_where = " AND kacamatan_kode = :kacamatan_kode"

        sql_text = """
        SELECT DISTINCT wilayah.lvl, wilayah.zawa, wilayah.kode, wilayah.nama, wilayah.lvl_1, wilayah.lvl_2, wilayah.lvl_3
        , 0 baseline
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik.lahir_tanggal >= :tahun_lahir_1
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) usia_1
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik.lahir_tanggal >= :tahun_lahir_2 AND t_mustahik.lahir_tanggal < :tahun_lahir_1
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) usia_2
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik.lahir_tanggal >= :tahun_lahir_3 AND t_mustahik.lahir_tanggal < :tahun_lahir_2
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) usia_3
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik.lahir_tanggal >= :tahun_lahir_4 AND t_mustahik.lahir_tanggal < :tahun_lahir_3
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) usia_4
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik.lahir_tanggal >= :tahun_lahir_5 AND t_mustahik.lahir_tanggal < :tahun_lahir_4
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) usia_5
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik.lahir_tanggal >= :tahun_lahir_6 AND t_mustahik.lahir_tanggal < :tahun_lahir_5
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) usia_6
        , (
            SELECT COUNT(DISTINCT t_mustahik_bappenas.nik) 
            FROM t_mustahik_bappenas JOIN t_mustahik ON t_mustahik.nik = t_mustahik_bappenas.nik
            WHERE t_mustahik.lahir_tanggal < :tahun_lahir_6
            AND t_mustahik.tanggal_terima >= :tahun_awal 
            AND t_mustahik.tanggal_terima < :tahun_akhir 
            AND t_mustahik_bappenas.""" + sql_param_data + """ = wilayah.kode 
            AND (t_mustahik.laz_kode = wilayah.laz OR wilayah.laz IS NULL)
        ) usia_7
        FROM
        (
            SELECT m_provinsi.provinsi_kode zawa, m_provinsi.provinsi_kode kode, m_provinsi.provinsi_nama nama, t_dtsen_akses.laz_kode laz, 1 lvl,
            m_provinsi.provinsi_nama lvl_1, '-' lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, null kabkota_kode, null kacamatan_kode
            FROM m_provinsi
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_provinsi.provinsi_kode OR t_dtsen_wilayah.provinsi_kode IS NULL
            JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
            WHERE t_dtsen_akses.email = :email
            AND provinsi_aktif = 'y'
            UNION
            SELECT CONCAT(SUBSTRING(m_kabkota.kabkota_kode, 1, 2), '.', SUBSTRING(m_kabkota.kabkota_kode, 3, 2)) zawa, 
            m_kabkota.kabkota_kode kode, m_kabkota.kabkota_nama nama, t_dtsen_akses.laz_kode laz, 2 lvl,
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, null kacamatan_kode
            FROM m_kabkota
            JOIN m_provinsi ON m_provinsi.provinsi_kode = m_kabkota.provinsi_kode 
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_kabkota.provinsi_kode 
            AND (t_dtsen_wilayah.kabkota_kode = m_kabkota.kabkota_kode OR t_dtsen_wilayah.kabkota_kode IS NULL)
            JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
            WHERE t_dtsen_akses.email = :email
            AND kabkota_aktif = 'y'
            UNION
            SELECT CONCAT(SUBSTRING(m_kecamatan.kecamatan_kode, 1, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 3, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 5, 2)) zawa, 
            m_kecamatan.kecamatan_kode kode, m_kecamatan.kecamatan_nama nama, t_dtsen_akses.laz_kode laz, 3 lvl,
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, m_kecamatan.kecamatan_nama lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, m_kecamatan.kecamatan_kode
            FROM m_kecamatan
            JOIN m_kabkota ON m_kabkota.kabkota_kode = m_kecamatan.kabkota_kode
            JOIN m_provinsi ON m_provinsi.provinsi_kode = m_kabkota.provinsi_kode
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_kabkota.provinsi_kode 
            AND (t_dtsen_wilayah.kabkota_kode = m_kabkota.kabkota_kode OR t_dtsen_wilayah.kabkota_kode IS NULL)
            AND (t_dtsen_wilayah.kecamatan_kode = m_kecamatan.kecamatan_kode OR t_dtsen_wilayah.kecamatan_kode IS NULL)
            JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
            WHERE t_dtsen_akses.email = :email
            AND kecamatan_aktif = 'y'
            UNION
            SELECT DISTINCT t_mustahik.provinsi_kode zawa, t_mustahik.provinsi_kode kode, m_provinsi.provinsi_nama nama, t_dtsen_akses.laz_kode laz, 1 lvl,
            m_provinsi.provinsi_nama lvl_1, '-' lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, null kabkota_kode, null kacamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
            UNION
            SELECT DISTINCT CONCAT(SUBSTRING(m_kabkota.kabkota_kode, 1, 2), '.', SUBSTRING(m_kabkota.kabkota_kode, 3, 2)) zawa, 
            m_kabkota.kabkota_kode kode, m_kabkota.kabkota_nama nama, t_dtsen_akses.laz_kode laz, 2 lvl,
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, null kacamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
            JOIN m_kabkota ON m_kabkota.provinsi_kode = m_provinsi.provinsi_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
            UNION
            SELECT DISTINCT CONCAT(SUBSTRING(m_kecamatan.kecamatan_kode, 1, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 3, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 5, 2)) zawa, 
            m_kecamatan.kecamatan_kode kode, m_kecamatan.kecamatan_nama nama, t_dtsen_akses.laz_kode laz, 3 lvl, 
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, m_kecamatan.kecamatan_nama lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, m_kecamatan.kecamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
            JOIN m_kabkota ON m_kabkota.provinsi_kode = m_provinsi.provinsi_kode
            JOIN m_kecamatan ON m_kecamatan.kabkota_kode = m_kabkota.kabkota_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
        ) wilayah
        WHERE wilayah.lvl = :sql_level
        """

        sql = text(sql_text + sql_where)

        result = db.session.execute(sql, {
            'tahun_awal'    : f'{tahun_awal}-01-01',
            'tahun_akhir'   : f'{tahun_akhir}-01-01',
            'tahun_lahir_1' : f'{tahun_lahir_1}-01-01',
            'tahun_lahir_2' : f'{tahun_lahir_2}-01-01',
            'tahun_lahir_3' : f'{tahun_lahir_3}-01-01',
            'tahun_lahir_4' : f'{tahun_lahir_4}-01-01',
            'tahun_lahir_5' : f'{tahun_lahir_5}-01-01',
            'tahun_lahir_6' : f'{tahun_lahir_6}-01-01',
            'email'         : email,
            'sql_level'     : sql_level,
            'provinsi_kode' : provinsi_kode,
            'kabkota_kode'  : kabkota_kode,
            'kacamatan_kode': kacamatan_kode
        }).mappings().all()

        return [dict(row) for row in result]
    
    @staticmethod
    def get_data_bidang(params: dict) -> list:
        tahun_awal = int(params.get("tahun") or datetime.now().year)
        tahun_akhir = int(params.get("tahun") or datetime.now().year) + 1
        email = (params.get("email") or '')
        provinsi_kode = (params.get("provinsi_kode") or None)
        kabkota_kode = (params.get("kabkota_kode") or None)
        kacamatan_kode = (params.get("kacamatan_kode") or None)

        sql_level = 1
        sql_where = ""

        if provinsi_kode:
            sql_level = 2
            sql_where = " AND provinsi_kode = :provinsi_kode"

        if kabkota_kode:
            sql_level = 3
            sql_where = " AND kabkota_kode = :kabkota_kode"

        if kacamatan_kode:
            sql_level = 3
            sql_where = " AND kacamatan_kode = :kacamatan_kode"

        sql_text = """
        SELECT
            b.bidang_kode,
            UPPER(b.bidang_label) AS bidang_label,
            COALESCE(x.total_penyaluran,0) AS total_penyaluran,
            COALESCE(x.total_mustahik,0) AS total_mustahik
        FROM m_bidang b
        LEFT JOIN
        (
            SELECT t_program.bidang_kode, SUM(wilayah.rupiah) total_penyaluran, COUNT(DISTINCT wilayah.mustahik) total_mustahik
            FROM
            (
                SELECT DISTINCT 1 lvl, t_mustahik.provinsi_kode kode, t_dtsen_akses.laz_kode laz, t_mustahik.program_kode, SUM(t_mustahik.rupiah) rupiah, COUNT(DISTINCT t_mustahik.nik) mustahik
                FROM t_mustahik
                JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
                JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
                JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
                WHERE t_dtsen_akses.email = :email
                AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
                GROUP BY lvl, kode, laz, program_kode
                UNION
                SELECT DISTINCT 2 lvl, t_mustahik.kabkota_kode kode, t_dtsen_akses.laz_kode laz, t_mustahik.program_kode, SUM(t_mustahik.rupiah) rupiah, COUNT(DISTINCT t_mustahik.nik) mustahik
                FROM t_mustahik
                JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
                JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
                JOIN m_kabkota ON m_kabkota.provinsi_kode = m_provinsi.provinsi_kode
                JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
                WHERE t_dtsen_akses.email = :email
                AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
                GROUP BY lvl, kode, laz, program_kode
                UNION
                SELECT DISTINCT 3 lvl, t_mustahik.kecamatan_kode kode, t_dtsen_akses.laz_kode laz, t_mustahik.program_kode, SUM(t_mustahik.rupiah) rupiah, COUNT(DISTINCT t_mustahik.nik) mustahik
                FROM t_mustahik
                JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil < 5
                JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.provinsi_kode
                JOIN m_kabkota ON m_kabkota.provinsi_kode = m_provinsi.provinsi_kode
                JOIN m_kecamatan ON m_kecamatan.kabkota_kode = m_kabkota.kabkota_kode
                JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
                WHERE t_dtsen_akses.email = :email
                AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir
                GROUP BY lvl, kode, laz, program_kode
            ) wilayah
            JOIN t_program ON t_program.program_kode = wilayah.program_kode
            WHERE wilayah.lvl = :sql_level 
            """ + sql_where + """ 
            GROUP BY t_program.bidang_kode
        ) x
        ON x.bidang_kode = b.bidang_kode
        ORDER BY b.is_prioritas DESC, b.bidang_kode
        """

        sql = text(sql_text)

        result = db.session.execute(sql, {
            'tahun_awal'    : f'{tahun_awal}-01-01',
            'tahun_akhir'   : f'{tahun_akhir}-01-01',
            'email'         : email,
            'sql_level'     : sql_level,
            'provinsi_kode' : provinsi_kode,
            'kabkota_kode'  : kabkota_kode,
            'kacamatan_kode': kacamatan_kode
        }).mappings().all()

        return [dict(row) for row in result]