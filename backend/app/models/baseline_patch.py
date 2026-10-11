from datetime import datetime
from ..extensions import db
from sqlalchemy import text

DATA_PROVINSI = """
    SELECT regexp_replace(t_dtsen_wilayah.provinsi_kode, '(\d{2})(?=\d)', '\1.', 'g') kode, m_provinsi.provinsi_nama nama
    FROM t_dtsen_akses
    JOIN t_dtsen_wilayah ON t_dtsen_wilayah.dtsen_akses_id = t_dtsen_akses.dtsen_akses_id
    JOIN t_laz ON (t_laz.laz_kode = t_dtsen_akses.laz_kode OR t_dtsen_akses.laz_kode IS NULL)
    JOIN m_provinsi ON m_provinsi.provinsi_kode = t_dtsen_wilayah.provinsi_kode
    WHERE t_dtsen_akses.email = :email
    UNION
    SELECT DISTINCT regexp_replace(ktp_provinsi_kode, '(\d{2})(?=\d)', '\1.', 'g') kode, m_provinsi.provinsi_nama nama
    FROM t_mustahik
    JOIN m_provinsi ON m_provinsi.provinsi_kode = ktp_provinsi_kode
    JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode
    WHERE t_dtsen_akses.email = :email
    AND YEAR(t_mustahik.tanggal_terima) = :tahun
"""

DATA_KABKOTA = """
    SELECT DISTINCT regexp_replace(m_kabkota.kabkota_kode, '(\d{2})(?=\d)', '\1.', 'g') kode, m_kabkota.kabkota_nama nama
    FROM m_kabkota
    JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_kabkota.provinsi_kode
    JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
    WHERE (t_dtsen_wilayah.kabkota_kode = m_kabkota.kabkota_kode OR t_dtsen_wilayah.kabkota_kode IS NULL)
    AND (t_dtsen_wilayah.provinsi_kode = :provinsi_kode OR t_dtsen_wilayah.provinsi_kode IS NULL)
    AND t_dtsen_akses.email = :email
    UNION
    SELECT DISTINCT regexp_replace(ktp_kabkota_kode, '(\d{2})(?=\d)', '\1.', 'g') kode, m_kabkota.kabkota_nama nama
    FROM t_mustahik
    JOIN m_kabkota ON m_kabkota.kabkota_kode = ktp_kabkota_kode
    JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode
    WHERE t_dtsen_akses.email = :email
    AND YEAR(t_mustahik.tanggal_terima) = :tahun
"""

DATA_KECAMATAN = """
    SELECT DISTINCT regexp_replace(m_kecamatan.kecamatan_kode, '(\d{2})(?=\d)', '\1.', 'g') kode, m_kecamatan.kecamatan_nama nama
    FROM m_kecamatan
    LEFT JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = LEFT(m_kecamatan.kabkota_kode,2)
    JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
    WHERE (t_dtsen_wilayah.kecamatan_kode = m_kecamatan.kecamatan_kode OR t_dtsen_wilayah.kecamatan_kode IS NULL)
    AND t_dtsen_akses.email = :email
    AND m_kecamatan.kabkota_kode = :kabkota_kode
    UNION
    SELECT DISTINCT regexp_replace(ktp_kecamatan_kode, '(\d{2})(?=\d)', '\1.', 'g') kode, m_kecamatan.kecamatan_nama nama
    FROM t_mustahik
    JOIN m_kecamatan ON m_kecamatan.kecamatan_kode = ktp_kecamatan_kode
    JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode
    WHERE t_dtsen_akses.email = :email
    AND YEAR(t_mustahik.tanggal_terima) = :tahun
"""

DATA_KELURAHAN = """
    SELECT DISTINCT regexp_replace(m_kelurahan.kelurahan_kode, '(\d{2})(?=\d)', '\1.', 'g') kode, m_kelurahan.kelurahan_nama nama
    FROM m_kelurahan
    LEFT JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = LEFT(m_kelurahan.kecamatan_kode,2)
    JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
    WHERE (t_dtsen_wilayah.kecamatan_kode = m_kelurahan.kecamatan_kode OR t_dtsen_wilayah.kecamatan_kode IS NULL)
    AND t_dtsen_akses.email = :email
    AND m_kelurahan.kecamatan_kode = :kecamatan_kode
    UNION
    SELECT DISTINCT regexp_replace(ktp_kelurahan_kode, '(\d{2})(?=\d)', '\1.', 'g') kode, m_kelurahan.kelurahan_nama nama
    FROM t_mustahik
    JOIN m_kelurahan ON m_kelurahan.kelurahan_kode = ktp_kelurahan_kode
    JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode
    WHERE t_dtsen_akses.email = :email
    AND YEAR(t_mustahik.tanggal_terima) = :tahun
"""

class BaselinePatch:
    
    @staticmethod
    def get_param_provinsi(params: dict) -> list:
        tahun = int(params.get("tahun") or datetime.now().year)
        email = (params.get("email") or '')

        sql = text(DATA_PROVINSI + " ORDER BY nama; ")

        result = db.session.execute(sql, {
            'email': email,
            'tahun': tahun
        }).mappings().all()

        return [dict(row) for row in result]
    
    @staticmethod
    def get_param_kabkota(params: dict) -> list:
        tahun = int(params.get("tahun") or datetime.now().year)
        email = (params.get("email") or '')
        provinsi_kode = (params.get("provinsi_kode") or "").replace(".", "") or None

        sql = text(DATA_KABKOTA + " ORDER BY nama; ")

        result = db.session.execute(sql, {
            'provinsi_kode': provinsi_kode,
            'email': email,
            'tahun': tahun
        }).mappings().all()

        return [dict(row) for row in result]
 
    @staticmethod
    def get_param_kecamatan(params: dict) -> list:
        tahun = int(params.get("tahun") or datetime.now().year)
        email = (params.get("email") or '')
        kabkota_kode = (params.get("kabkota_kode") or "").replace(".", "") or None

        sql = text(DATA_KECAMATAN + " ORDER BY nama; ")

        result = db.session.execute(sql, {
            'kabkota_kode': kabkota_kode,
            'email': email,
            'tahun': tahun
        }).mappings().all()

        return [dict(row) for row in result]
    
    @staticmethod
    def get_table_anggota(params: dict) -> list:
        email = (params.get("email") or '')
        lembaga = (params.get("lembaga") or None)
        provinsi_kode = (params.get("provinsi_kode") or None)
        kabkota_kode = (params.get("kabkota_kode") or None)
        kecamatan_kode = (params.get("kecamatan_kode") or None)

        sql_level = 1
        sql_param_data = "ktp_provinsi_kode"
        sql_where = ""
        sql_laz = ""

        if lembaga:
            sql_laz = " AND t_mustahik.laz_kode = :lembaga"

        if provinsi_kode:
            sql_level = 2
            sql_param_data = "ktp_kabkota_kode"
            sql_where = " AND provinsi_kode = :provinsi_kode"

        if kabkota_kode:
            sql_level = 3
            sql_param_data = "ktp_kecamatan_kode"
            sql_where = " AND kabkota_kode = :kabkota_kode"

        if kecamatan_kode:
            sql_level = 3
            sql_param_data = "ktp_kecamatan_kode"
            sql_where = " AND kecamatan_kode = :kecamatan_kode"

        sql_text = """
        SELECT DISTINCT *
        FROM
        (
            SELECT m_provinsi.provinsi_kode zawa, m_provinsi.provinsi_kode kode, m_provinsi.provinsi_nama nama, t_dtsen_akses.laz_kode laz, 1 lvl,
            m_provinsi.provinsi_nama lvl_1, '-' lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, null kabkota_kode, null kecamatan_kode
            FROM m_provinsi
            JOIN t_dtsen_wilayah ON t_dtsen_wilayah.provinsi_kode = m_provinsi.provinsi_kode OR t_dtsen_wilayah.provinsi_kode IS NULL
            JOIN t_dtsen_akses ON t_dtsen_akses.dtsen_akses_id = t_dtsen_wilayah.dtsen_akses_id
            WHERE t_dtsen_akses.email = :email
            AND provinsi_aktif = 'y'
            UNION
            SELECT CONCAT(SUBSTRING(m_kabkota.kabkota_kode, 1, 2), '.', SUBSTRING(m_kabkota.kabkota_kode, 3, 2)) zawa, 
            m_kabkota.kabkota_kode kode, m_kabkota.kabkota_nama nama, t_dtsen_akses.laz_kode laz, 2 lvl,
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, null kecamatan_kode
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
            SELECT DISTINCT t_mustahik.ktp_provinsi_kode zawa, t_mustahik.ktp_provinsi_kode kode, m_provinsi.provinsi_nama nama, t_dtsen_akses.laz_kode laz, 1 lvl,
            m_provinsi.provinsi_nama lvl_1, '-' lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, null kabkota_kode, null kecamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil BETWEEN 1 AND 4
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.ktp_provinsi_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir 
            """ + sql_laz + """ 
            UNION
            SELECT DISTINCT CONCAT(SUBSTRING(m_kabkota.kabkota_kode, 1, 2), '.', SUBSTRING(m_kabkota.kabkota_kode, 3, 2)) zawa, 
            m_kabkota.kabkota_kode kode, m_kabkota.kabkota_nama nama, t_dtsen_akses.laz_kode laz, 2 lvl,
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, '-' lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, null kecamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil BETWEEN 1 AND 4
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.ktp_provinsi_kode
            JOIN m_kabkota ON m_kabkota.provinsi_kode = m_provinsi.provinsi_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir 
            """ + sql_laz + """ 
            UNION
            SELECT DISTINCT CONCAT(SUBSTRING(m_kecamatan.kecamatan_kode, 1, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 3, 2), '.', SUBSTRING(m_kecamatan.kecamatan_kode, 5, 2)) zawa, 
            m_kecamatan.kecamatan_kode kode, m_kecamatan.kecamatan_nama nama, t_dtsen_akses.laz_kode laz, 3 lvl, 
            m_provinsi.provinsi_nama lvl_1, m_kabkota.kabkota_nama lvl_2, m_kecamatan.kecamatan_nama lvl_3, m_provinsi.provinsi_kode, m_kabkota.kabkota_kode, m_kecamatan.kecamatan_kode
            FROM t_mustahik
            JOIN t_mustahik_bappenas ON t_mustahik_bappenas.nik = t_mustahik.nik AND t_mustahik_bappenas.desil BETWEEN 1 AND 4
            JOIN m_provinsi ON m_provinsi.provinsi_kode = t_mustahik.ktp_provinsi_kode
            JOIN m_kabkota ON m_kabkota.provinsi_kode = m_provinsi.provinsi_kode
            JOIN m_kecamatan ON m_kecamatan.kabkota_kode = m_kabkota.kabkota_kode
            JOIN t_dtsen_akses ON t_dtsen_akses.laz_kode = t_mustahik.laz_kode OR t_dtsen_akses.laz_kode IS NULL
            WHERE t_dtsen_akses.email = :email
            AND t_mustahik.tanggal_terima >= :tahun_awal AND t_mustahik.tanggal_terima < :tahun_akhir 
            """ + sql_laz + """ 
        ) wilayah
        WHERE wilayah.lvl = :sql_level
        """

        sql = text(sql_text + sql_where)

        result = db.session.execute(sql, {
            'tahun_awal'    : f'{tahun_awal}-01-01',
            'tahun_akhir'   : f'{tahun_akhir}-01-01',
            'email'         : email,
            'lembaga'       : lembaga,
            'sql_level'     : sql_level,
            'provinsi_kode' : provinsi_kode,
            'kabkota_kode'  : kabkota_kode,
            'kecamatan_kode': kecamatan_kode
        }).mappings().all()

        return [dict(row) for row in result]