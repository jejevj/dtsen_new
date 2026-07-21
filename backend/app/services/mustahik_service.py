import hashlib
from datetime import date
from babel.dates import format_date
from ..models.mustahik import Mustahik
from ..models.laz import Laz
from ..models.program import Program
from ..models.wilayah import Provinsi, KabKota, Kecamatan, Kelurahan
from ..schemas.mustahik import MustahikSchema, MustahikDetailSchema
from ..extensions import db
from sqlalchemy import text
from datetime import date, datetime
import time
import base64

mustahik_schema = MustahikSchema()
mustahiks_schema = MustahikSchema(many=True)
mustahik_detail_schema = MustahikDetailSchema(many=True)


SKALA_MAP = {
    1: 'Nasional',
    2: 'Provinsi',
    3: 'Kabupaten/Kota',
}

GENDER_MAP = {
    'm': 'Laki - Laki',
    'f': 'Perempuan',
}

METODE_MAP = {
    'pml': 'Penerima Manfaat Langsung',
    'pmtl': 'Penerima Manfaat Tidak Langsung',
}

KAWIN_MAP = {
    'kw': 'Kawin',
    'bk': 'Belum Kawin',
    'cm': 'Cerai Mati',
    'ch': 'Cerai Hidup',
}

def _mask_nik(nik):
    if not nik:
        return None
    nik = str(nik)
    if len(nik) <= 7:
        return nik
    return f"{nik[:6]}{'*' * (len(nik) - 7)}{nik[-1]}"

def _hitung_usia(tanggal_lahir):
    if not tanggal_lahir:
        return None

    # jika masih berupa string
    if isinstance(tanggal_lahir, str):
        try:
            tanggal_lahir = datetime.strptime(tanggal_lahir, "%Y-%m-%d").date()
        except ValueError:
            return None

    hari_ini = date.today()

    usia = hari_ini.year - tanggal_lahir.year
    if (hari_ini.month, hari_ini.day) < (tanggal_lahir.month, tanggal_lahir.day):
        usia -= 1

    return usia

def _format_tanggal(d) -> str | None:
    """Format date ke DD MMMM YYYY bahasa Indonesia."""
    if d is None:
        return None
    if isinstance(d, str):
        try:
            d = date.fromisoformat(d)
        except ValueError:
            return d
    try:
        return format_date(d, format='dd MMMM yyyy', locale='id_ID')
    except Exception:
        return str(d)


class MustahikService:

    @staticmethod
    def get_list(params: dict) -> dict:

        where = [
            "l.laz_status IN ('aktif','daftar_ulang')"
        ]
        bind = {}
        if params.get("nama"):
            where.append("m.nama_lengkap LIKE :nama")
            bind["nama"] = f"%{params['nama']}%"

        if params.get("nik"):
            where.append("m.nik = :nik")
            bind["nik"] = params["nik"]

        if params.get("kk"):
            where.append("m.kk = :kk")
            bind["kk"] = params["kk"]

        if params.get("jenis_kelamin"):
            where.append("m.jenis_kelamin=:jenis_kelamin")
            bind["jenis_kelamin"] = params["jenis_kelamin"]

        if params.get("agama"):
            where.append("m.agama=:agama")
            bind["agama"] = params["agama"]

        if params.get("laz_kode"):
            where.append("m.laz_kode=:laz_kode")
            bind["laz_kode"] = params["laz_kode"]

        if params.get("skala_laz"):
            where.append("l.skala=:skala_laz")
            bind["skala_laz"] = params["skala_laz"]

        if params.get("program_kode"):
            where.append("p.bidang_kode=:program_kode")
            bind["program_kode"] = params["program_kode"]


        if params.get("tipe_penerimaan"):
            where.append("m.tipe_penerimaan=:tipe_penerimaan")
            bind["tipe_penerimaan"] = params["tipe_penerimaan"]

        if params.get("jumlah_penyaluran_min"):
            where.append("""
            (
                SELECT SUM(mx.rupiah)
                FROM t_mustahik mx
                WHERE mx.nik = m.nik
                AND (
                    :laz_kode IS NULL
                    OR mx.laz_kode = :laz_kode
                )
            ) >= :jumlah_min
            """)
            bind["jumlah_min"] = params["jumlah_penyaluran_min"]

        if params.get("jumlah_penyaluran_max"):
            where.append("""
            (
                SELECT SUM(mx.rupiah)
                FROM t_mustahik mx
                WHERE mx.nik = m.nik
                AND (
                    :laz_kode IS NULL
                    OR mx.laz_kode = :laz_kode
                )
            ) <= :jumlah_max
            """)
            bind["jumlah_max"] = params["jumlah_penyaluran_max"]

        if params.get("provinsi_kode_domisili"):
            where.append("m.provinsi_kode=:provinsi")
            bind["provinsi"] = params["provinsi_kode_domisili"]

        if params.get("kabkota_kode_domisili"):
            where.append("m.kabkota_kode=:kab")
            bind["kab"] = params["kabkota_kode_domisili"]

        if params.get("kecamatan_kode_domisili"):
            where.append("m.kecamatan_kode=:kec")
            bind["kec"] = params["kecamatan_kode_domisili"]

        if params.get("kelurahan_kode_domisili"):
            where.append("m.kelurahan_kode=:kel")
            bind["kel"] = params["kelurahan_kode_domisili"]

       
        if params.get("provinsi_kode"):
            where.append("m.ktp_provinsi_kode=:ktp_prov")
            bind["ktp_prov"] = params["provinsi_kode"]

        if params.get("kabkota_kode"):
            where.append("m.ktp_kabkota_kode=:ktp_kab")
            bind["ktp_kab"] = params["kabkota_kode"]

        if params.get("kecamatan_kode"):
            where.append("m.ktp_kecamatan_kode=:ktp_kec")
            bind["ktp_kec"] = params["kecamatan_kode"]

        if params.get("kelurahan_kode"):
            where.append("m.ktp_kelurahan_kode=:ktp_kel")
            bind["ktp_kel"] = params["kelurahan_kode"]

        if params.get("usia_min"):
            where.append("""
                TIMESTAMPDIFF(YEAR,m.lahir_tanggal,CURDATE())>=:usia_min
            """)
            bind["usia_min"] = params["usia_min"]

        if params.get("usia_max"):
            where.append("""
                TIMESTAMPDIFF(YEAR,m.lahir_tanggal,CURDATE())<=:usia_max
            """)
            bind["usia_max"] = params["usia_max"]


        if params.get("desil"):
            where.append("COALESCE(b.desil,1)=:desil")
            bind["desil"] = params["desil"]

        if params.get("nama_program"):
            where.append("p.program_nama LIKE :program_nama")
            bind["program_nama"] = f"%{params['nama_program']}%"

        where_sql = " AND ".join(where)
        page = int(params.get("page",1))
        per_page = int(params.get("per_page",20))

        offset = (page-1)*per_page

        bind["limit"] = per_page
        bind["offset"] = offset

        total_sql = text(f"""
            SELECT COUNT(DISTINCT m.nik) total
            FROM t_mustahik m
            INNER JOIN t_laz l ON m.laz_kode=l.laz_kode
            INNER JOIN t_program p ON m.program_kode=p.program_kode
            LEFT JOIN t_mustahik_bappenas b ON b.nik=m.nik
            WHERE {where_sql}
        """)

        total = db.session.execute(total_sql,bind).scalar()

        sql = text(f"""
        SELECT
            MIN(m.mustahik_id) AS mustahik_id,
            m.nik,
            MAX(m.nama_lengkap) AS nama_lengkap,
            MAX(m.jenis_kelamin) AS jenis_kelamin,
            MAX(m.lahir_tanggal) AS lahir_tanggal,
            SUM(m.rupiah) AS rupiah,
            MAX(m.kk) AS kk,
            MAX(prov.provinsi_nama) AS provinsi_nama,
            MAX(kab.kabkota_nama) AS kabkota_nama,
            MAX(l.laz_nama) AS laz_nama,
            MAX(l.skala) AS skala,
            MAX(p.program_nama) AS program_nama,
            COALESCE(MAX(b.desil),1) AS desil,
            MAX(m.created_at) AS created_at
        FROM t_mustahik m
        INNER JOIN t_laz l ON m.laz_kode=l.laz_kode
        INNER JOIN t_program p ON m.program_kode=p.program_kode
        LEFT JOIN t_mustahik_bappenas b ON b.nik=m.nik
        LEFT JOIN m_provinsi prov ON m.ktp_provinsi_kode=prov.provinsi_kode
        LEFT JOIN m_kabkota kab ON m.ktp_kabkota_kode=kab.kabkota_kode
        WHERE {where_sql}
        GROUP BY m.nik
        ORDER BY MAX(m.created_at) DESC
        LIMIT :limit OFFSET :offset
        """)
        rows = db.session.execute(sql,bind).mappings().all()
        items=[]
        for row in rows:
            items.append({
                "mustahik_id":row["mustahik_id"],
                "nik": _mask_nik(row["nik"]),
                "nik_hashed":base64.urlsafe_b64encode(str(row["nik"]).encode()).decode(),
                "nama_lengkap":row["nama_lengkap"],
                "jenis_kelamin":row["jenis_kelamin"],
                "usia":_hitung_usia(row["lahir_tanggal"]),
                "provinsi_nama":row["provinsi_nama"],
                "kabkota_nama":row["kabkota_nama"],
                "desil":row["desil"]
            })
        return {
            "data": items,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }

    @staticmethod
    def get_detail(nik_hashed: str) -> dict:
        nik_dec = base64.urlsafe_b64decode(nik_hashed.encode()).decode()
        sql = text("""
            SELECT
                m.*,
                l.laz_nama,
                l.skala,
                p.program_nama,
                prov.provinsi_nama,
                kab.kabkota_nama,
                kec.kecamatan_nama,
                kel.kelurahan_nama,
                ktp_prov.provinsi_nama  AS ktp_provinsi_nama,
                ktp_kab.kabkota_nama    AS ktp_kabkota_nama,
                ktp_kec.kecamatan_nama  AS ktp_kecamatan_nama,
                ktp_kel.kelurahan_nama  AS ktp_kelurahan_nama,
                '1' AS desil
            FROM t_mustahik m
            INNER JOIN t_laz l ON m.laz_kode = l.laz_kode
            INNER JOIN t_program p ON m.program_kode = p.program_kode
            LEFT JOIN m_provinsi prov ON m.provinsi_kode = prov.provinsi_kode
            LEFT JOIN m_kabkota kab ON m.kabkota_kode = kab.kabkota_kode
            LEFT JOIN m_kecamatan kec ON m.kecamatan_kode = kec.kecamatan_kode
            LEFT JOIN m_kelurahan kel ON m.kelurahan_kode = kel.kelurahan_kode
            LEFT JOIN m_provinsi ktp_prov ON m.ktp_provinsi_kode = ktp_prov.provinsi_kode
            LEFT JOIN m_kabkota ktp_kab ON m.ktp_kabkota_kode = ktp_kab.kabkota_kode
            LEFT JOIN m_kecamatan ktp_kec ON m.ktp_kecamatan_kode = ktp_kec.kecamatan_kode
            LEFT JOIN m_kelurahan ktp_kel ON m.ktp_kelurahan_kode = ktp_kel.kelurahan_kode
            WHERE l.laz_status IN ('aktif','daftar_ulang')
                AND m.nik = :nik_dec
            ORDER BY m.created_at DESC
        """)

        rows = db.session.execute(
            sql,
            {
                "nik_dec": nik_dec
            }
        ).mappings().all()

        if not rows:
            return {
                "message": "Data tidak ditemukan.",
                "status_code": 404
            }

        items = []

        for row in rows:
            items.append({
                "nik": str(row["nik"]) if row["nik"] else None,
                "nik_hashed": base64.urlsafe_b64encode(str(row["nik"]).encode()).decode() if row["nik"] else None,
                "kk": row["kk"],
                "nama_lengkap": row["nama_lengkap"],
                "jenis_kelamin": GENDER_MAP.get(row["jenis_kelamin"], row["jenis_kelamin"]),
                "lahir_tanggal": _format_tanggal(row["lahir_tanggal"]),
                "agama": row["agama"],
                "rupiah": str(row["rupiah"]),
                "tipe_penerimaan": row["tipe_penerimaan"],
                "tanggal_terima": str(row["tanggal_terima"]) if row["tanggal_terima"] else None,
                "created_at": str(row["created_at"]) if row["created_at"] else None,
                "laz_kode": row["laz_kode"],
                "laz_nama": row["laz_nama"],
                "skala": SKALA_MAP.get(row["skala"], str(row["skala"])) if row["skala"] else None,
                "program_kode": row["program_kode"],
                "program_nama": row["program_nama"],
                "alamat_domisili": row["alamat_domisili"],
                "provinsi_nama": row["provinsi_nama"],
                "kabkota_nama": row["kabkota_nama"],
                "kecamatan_nama": row["kecamatan_nama"],
                "kelurahan_nama": row["kelurahan_nama"],
                "ktp_alamat": row["ktp_alamat"],
                "ktp_provinsi_nama": row["ktp_provinsi_nama"],
                "ktp_kabkota_nama": row["ktp_kabkota_nama"],
                "ktp_kecamatan_nama": row["ktp_kecamatan_nama"],
                "ktp_kelurahan_nama": row["ktp_kelurahan_nama"],
                "desil": row["desil"],
                "usia": _hitung_usia(row["lahir_tanggal"]),
                "tanggungan": row["tanggungan"],
                "status_pernikahan": KAWIN_MAP.get(row["kawin_status"], row["kawin_status"]),
            })

        return {
            "data": items
        }
    
    @staticmethod
    def get_riwayat(nik_hashed: str):
        nik_dec = base64.urlsafe_b64decode(nik_hashed.encode()).decode()
        sql = text("""
            SELECT
                m.tanggal_terima,
                m.tipe_penerimaan,
                m.rupiah,
                p.program_nama,
                COALESCE(l.laz_nama, u.uker_nama) AS lembaga,
                m.created_at,
                b.bidang_label,
                m.laz_kode
            FROM t_mustahik m
            INNER JOIN t_program p
                ON m.program_kode = p.program_kode
            LEFT JOIN t_laz l
                ON m.laz_kode = l.laz_kode
            LEFT JOIN m_uker u
                ON m.laz_kode = u.uker_kode
            LEFT JOIN m_bidang b
                ON p.bidang_kode = b.bidang_kode
            WHERE
                m.nik = :nik_dec
                AND l.laz_status IN ('aktif','daftar_ulang')
            ORDER BY m.tanggal_terima DESC
        """)

        rows = db.session.execute(
            sql,
            {"nik_dec": nik_dec}
        ).mappings().all()
        data = []

        for row in rows:
            tanggal = row["tanggal_terima"]
            data.append({
                "tahun": tanggal.year if tanggal else None,
                "periode": _format_tanggal(tanggal),
                "program": row["program_nama"],
                "nominal": row["rupiah"],
                "metode": METODE_MAP.get(row["tipe_penerimaan"], row["tipe_penerimaan"]),
                "status": "Tersalurkan",
                "tanggal": _format_tanggal(tanggal),
                "laz": row["lembaga"],
                "laz_kode": row["laz_kode"],
                "bidang": row["bidang_label"]
            })
        return {
            "data": data
        }

    @staticmethod
    def get_program(nik_hashed: str):
        sql = text("""
            SELECT
                m.program_kode,
                p.program_nama,
                b.bidang_label
            FROM t_mustahik m
            INNER JOIN t_program p
                ON m.program_kode = p.program_kode
            INNER JOIN m_bidang b
                ON p.bidang_kode = b.bidang_kode
            WHERE md5(CAST(m.nik AS CHAR)) = :nik_hashed
            ORDER BY b.bidang_label, p.program_nama
        """)

        rows = db.session.execute(
            sql,
            {"nik_hashed": nik_hashed}
        ).mappings().all()
        data = []
        for row in rows:
            data.append({
                "program_kode": row["program_kode"],
                "program_nama": row["program_nama"],
                "bidang": row["bidang_label"]
            })

        return {
            "data": data
        }

    