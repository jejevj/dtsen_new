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
        query = Mustahik.query

        # --- Filter individu (kategori=individu di tampilan_dtsen) ---
        if params.get('nama'):
            query = query.filter(Mustahik.nama_lengkap.ilike(f"%{params['nama']}%"))
        if params.get('nik'):
            query = query.filter(Mustahik.nik == str(params['nik']))
        if params.get('jenis_kelamin'):
            query = query.filter_by(jenis_kelamin=params['jenis_kelamin'])
        if params.get('agama'):
            query = query.filter_by(agama=params['agama'])

        # --- Penerimaan ---
        if params.get('laz_kode'):
            query = query.filter_by(laz_kode=params['laz_kode'])
        if params.get('program_kode'):
            query = query.filter_by(program_kode=params['program_kode'])
        if params.get('tipe_penerimaan'):
            query = query.filter_by(tipe_penerimaan=params['tipe_penerimaan'])
        if params.get('tanggal_terima'):
            query = query.filter_by(tanggal_terima=params['tanggal_terima'])

        # --- Wilayah ---
        if params.get('provinsi_kode'):
            query = query.filter_by(provinsi_kode=params['provinsi_kode'])
        if params.get('kabkota_kode'):
            query = query.filter_by(kabkota_kode=params['kabkota_kode'])

        page     = int(params.get('page', 1))
        per_page = int(params.get('per_page', 20))
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'data': mustahiks_schema.dump(paginated.items),
            'meta': {
                'page':     paginated.page,
                'per_page': paginated.per_page,
                'total':    paginated.total,
                'pages':    paginated.pages,
            }
        }

    @staticmethod
    def get_detail(nik_hashed: str) -> dict:
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
                AND md5(CAST(m.nik AS CHAR)) = :nik_hashed
            ORDER BY m.created_at DESC
        """)

        rows = db.session.execute(
            sql,
            {
                "nik_hashed": nik_hashed
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
                "nik_hashed": hashlib.md5(str(row["nik"]).encode()).hexdigest() if row["nik"] else None,
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
        sql = text("""
            SELECT
                m.tanggal_terima,
                m.tipe_penerimaan,
                m.rupiah,
                p.program_nama,
                l.laz_nama,
                m.created_at,
                b.bidang_label
            FROM t_mustahik m
            INNER JOIN t_program p
                ON m.program_kode = p.program_kode
            INNER JOIN t_laz l
                ON m.laz_kode = l.laz_kode
            LEFT JOIN m_bidang b
                ON p.bidang_kode = b.bidang_kode
            WHERE
                md5(CAST(m.nik AS CHAR)) = :nik_hashed
                AND l.laz_status IN ('aktif','daftar_ulang')
            ORDER BY m.tanggal_terima DESC
        """)

        rows = db.session.execute(
            sql,
            {"nik_hashed": nik_hashed}
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
                "laz": row["laz_nama"],
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