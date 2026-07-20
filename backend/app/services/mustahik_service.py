import hashlib
from datetime import date
from babel.dates import format_date
from sqlalchemy import text
from ..models.mustahik import Mustahik
from ..models.laz import Laz
from ..models.program import Program
from ..models.wilayah import Provinsi, KabKota, Kecamatan, Kelurahan
from ..schemas.mustahik import MustahikSchema, MustahikDetailSchema
from ..extensions import db

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
    'M': 'Laki - Laki',
    'F': 'Perempuan',
}


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


def _apply_lag_dedup(items: list[dict]) -> list[dict]:
    """
    Replicate LAG() window deduplication dari getReallyDetaiMustahikNotHashed:
    jika nilai sama dengan baris sebelumnya, set ke None.
    """
    for i in range(1, len(items)):
        prev = items[i - 1]
        curr = items[i]
        if curr['nama_lengkap'] == prev['nama_lengkap']:
            curr['nama_lengkap'] = None
        if curr['jenis_kelamin'] == prev['jenis_kelamin'] and curr['laz_nama'] == prev['laz_nama']:
            curr['jenis_kelamin'] = None
        if curr['agama'] == prev['agama']:
            curr['agama'] = None
        if curr['nik'] == prev['nik']:
            curr['nik'] = None
    return items


class MustahikService:
    @staticmethod
    def get_list(params: dict) -> dict:
        query = Mustahik.query

        if params.get('nama'):
            query = query.filter(Mustahik.nama_lengkap.ilike(f"%{params['nama']}%"))
        if params.get('nik'):
            query = query.filter(Mustahik.nik == str(params['nik']))
        if params.get('jenis_kelamin'):
            query = query.filter_by(jenis_kelamin=params['jenis_kelamin'])
        if params.get('agama'):
            query = query.filter_by(agama=params['agama'])
        if params.get('laz_kode'):
            query = query.filter_by(laz_kode=params['laz_kode'])
        if params.get('program_kode'):
            query = query.filter_by(program_kode=params['program_kode'])
        if params.get('tipe_penerimaan'):
            query = query.filter_by(tipe_penerimaan=params['tipe_penerimaan'])
        if params.get('tanggal_terima'):
            query = query.filter_by(tanggal_terima=params['tanggal_terima'])
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
        """
        Ambil detail mustahik berdasarkan MD5(nik).
        """
        KtpProvinsi  = db.aliased(Provinsi,  name='ktp_provinsi')
        KtpKabKota   = db.aliased(KabKota,   name='ktp_kabkota')
        KtpKecamatan = db.aliased(Kecamatan, name='ktp_kecamatan')
        KtpKelurahan = db.aliased(Kelurahan, name='ktp_kelurahan')

        rows = (
            db.session.query(
                Mustahik,
                Laz.laz_nama,
                Laz.skala,
                Program.program_nama,
                Provinsi.provinsi_nama,
                KabKota.kabkota_nama,
                Kecamatan.kecamatan_nama,
                Kelurahan.kelurahan_nama,
                KtpProvinsi.provinsi_nama.label('ktp_provinsi_nama'),
                KtpKabKota.kabkota_nama.label('ktp_kabkota_nama'),
                KtpKecamatan.kecamatan_nama.label('ktp_kecamatan_nama'),
                KtpKelurahan.kelurahan_nama.label('ktp_kelurahan_nama'),
            )
            .join(Laz, Mustahik.laz_kode == Laz.laz_kode)
            .filter(Laz.laz_status.in_(['aktif', 'daftar_ulang']))
            .join(Program, Mustahik.program_kode == Program.program_kode)
            .outerjoin(Provinsi,      Mustahik.provinsi_kode      == Provinsi.provinsi_kode)
            .outerjoin(KabKota,       Mustahik.kabkota_kode       == KabKota.kabkota_kode)
            .outerjoin(Kecamatan,     Mustahik.kecamatan_kode     == Kecamatan.kecamatan_kode)
            .outerjoin(Kelurahan,     Mustahik.kelurahan_kode     == Kelurahan.kelurahan_kode)
            .outerjoin(KtpProvinsi,   Mustahik.ktp_provinsi_kode  == KtpProvinsi.provinsi_kode)
            .outerjoin(KtpKabKota,    Mustahik.ktp_kabkota_kode   == KtpKabKota.kabkota_kode)
            .outerjoin(KtpKecamatan,  Mustahik.ktp_kecamatan_kode == KtpKecamatan.kecamatan_kode)
            .outerjoin(KtpKelurahan,  Mustahik.ktp_kelurahan_kode == KtpKelurahan.kelurahan_kode)
            .filter(
                db.func.md5(db.cast(Mustahik.nik, db.String)) == nik_hashed
            )
            .order_by(Mustahik.created_at.desc())
            .all()
        )

        if not rows:
            return {'message': 'Data tidak ditemukan.', 'status_code': 404}

        items = []
        for (
            m, laz_nama, skala, program_nama,
            provinsi_nama, kabkota_nama, kecamatan_nama, kelurahan_nama,
            ktp_provinsi_nama, ktp_kabkota_nama, ktp_kecamatan_nama, ktp_kelurahan_nama,
        ) in rows:
            items.append({
                'nik':                str(m.nik),
                'nik_hashed':         hashlib.md5(str(m.nik).encode()).hexdigest(),
                'kk':                 m.kk,
                'nama_lengkap':       m.nama_lengkap,
                'jenis_kelamin':      GENDER_MAP.get(m.jenis_kelamin, m.jenis_kelamin),
                'lahir_tanggal':      _format_tanggal(m.lahir_tanggal),
                'agama':              m.agama,
                'rupiah':             str(m.rupiah),
                'tipe_penerimaan':    m.tipe_penerimaan,
                'tanggal_terima':     str(m.tanggal_terima) if m.tanggal_terima else None,
                'created_at':         str(m.created_at) if m.created_at else None,
                'laz_kode':           m.laz_kode,
                'laz_nama':           laz_nama,
                'skala':              SKALA_MAP.get(skala, str(skala)) if skala is not None else None,
                'program_kode':       m.program_kode,
                'program_nama':       program_nama,
                'alamat_domisili':    m.alamat_domisili,
                'provinsi_nama':      provinsi_nama,
                'kabkota_nama':       kabkota_nama,
                'kecamatan_nama':     kecamatan_nama,
                'kelurahan_nama':     kelurahan_nama,
                'ktp_alamat':         m.ktp_alamat,
                'ktp_provinsi_nama':  ktp_provinsi_nama,
                'ktp_kabkota_nama':   ktp_kabkota_nama,
                'ktp_kecamatan_nama': ktp_kecamatan_nama,
                'ktp_kelurahan_nama': ktp_kelurahan_nama,
            })

        _apply_lag_dedup(items)
        return {'data': mustahik_detail_schema.dump(items)}

    @staticmethod
    def get_detail_by_nik(nik: str) -> dict:
        """
        Ambil detail mustahik berdasarkan NIK plain (tidak di-hash).

        Strategi performa:
        - Gunakan raw SQL (text()) agar MySQL optimizer bisa memanfaatkan
          index pada kolom `nik` secara langsung (berbeda dengan MD5 yang
          function-based dan tidak bisa pakai index biasa).
        - Semua JOIN dilakukan dalam satu query untuk menghindari N+1.
        - LAG deduplication dilakukan di Python (sama persis dengan
          getReallyDetaiMustahikNotHashed di PHP).
        """
        sql = text("""
            SELECT
                a.mustahik_id,
                a.nik,
                a.kk,
                a.nama_lengkap,
                a.jenis_kelamin,
                a.lahir_tanggal,
                a.agama,
                a.kk,
                a.alamat_domisili,
                a.rupiah,
                a.tipe_penerimaan,
                a.tanggal_terima,
                a.created_at,
                a.laz_kode,
                a.program_kode,
                a.ktp_alamat,
                t.laz_nama,
                t.skala,
                p.program_nama,
                prov.provinsi_nama,
                k.kabkota_nama,
                mk.kecamatan_nama,
                ml.kelurahan_nama,
                ktp_provinsi.provinsi_nama   AS ktp_provinsi_nama,
                ktp_kabkota.kabkota_nama     AS ktp_kabkota_nama,
                ktp_kecamatan.kecamatan_nama AS ktp_kecamatan_nama,
                ktp_kelurahan.kelurahan_nama AS ktp_kelurahan_nama
            FROM t_mustahik AS a
            JOIN  t_laz     AS t   ON a.laz_kode      = t.laz_kode
                                  AND t.laz_status    IN ('aktif', 'daftar_ulang')
            JOIN  t_program AS p   ON a.program_kode  = p.program_kode
            LEFT JOIN m_provinsi   AS prov          ON a.provinsi_kode      = prov.provinsi_kode
            LEFT JOIN m_kabkota    AS k             ON a.kabkota_kode       = k.kabkota_kode
            LEFT JOIN m_kecamatan  AS mk            ON a.kecamatan_kode     = mk.kecamatan_kode
            LEFT JOIN m_kelurahan  AS ml            ON a.kelurahan_kode     = ml.kelurahan_kode
            LEFT JOIN m_provinsi   AS ktp_provinsi  ON a.ktp_provinsi_kode  = ktp_provinsi.provinsi_kode
            LEFT JOIN m_kabkota    AS ktp_kabkota   ON a.ktp_kabkota_kode   = ktp_kabkota.kabkota_kode
            LEFT JOIN m_kecamatan  AS ktp_kecamatan ON a.ktp_kecamatan_kode = ktp_kecamatan.kecamatan_kode
            LEFT JOIN m_kelurahan  AS ktp_kelurahan ON a.ktp_kelurahan_kode = ktp_kelurahan.kelurahan_kode
            WHERE a.nik = :nik
            ORDER BY a.created_at DESC
        """)

        rows = db.session.execute(sql, {'nik': nik}).mappings().all()

        if not rows:
            return {'message': 'Data tidak ditemukan.', 'status_code': 404}

        skala_map = {1: 'Nasional', 2: 'Provinsi', 3: 'Kabupaten/Kota'}
        gender_map = {'m': 'Laki - Laki', 'f': 'Perempuan', 'M': 'Laki - Laki', 'F': 'Perempuan'}

        items = []
        for row in rows:
            skala_raw = row['skala']
            skala_label = skala_map.get(skala_raw, str(skala_raw)) if skala_raw is not None else None

            jk_raw = row['jenis_kelamin']
            jk_label = gender_map.get(jk_raw, jk_raw) if jk_raw is not None else None

            items.append({
                'nik':                str(row['nik']) if row['nik'] else None,
                'nik_hashed':         hashlib.md5(str(row['nik']).encode()).hexdigest() if row['nik'] else None,
                'kk':                 row['kk'],
                'nama_lengkap':       row['nama_lengkap'],
                'jenis_kelamin':      jk_label,
                'lahir_tanggal':      _format_tanggal(row['lahir_tanggal']),
                'agama':              row['agama'],
                'rupiah':             str(row['rupiah']) if row['rupiah'] is not None else None,
                'tipe_penerimaan':    row['tipe_penerimaan'],
                'tanggal_terima':     str(row['tanggal_terima']) if row['tanggal_terima'] else None,
                'created_at':         str(row['created_at']) if row['created_at'] else None,
                'laz_kode':           row['laz_kode'],
                'laz_nama':           row['laz_nama'],
                'skala':              skala_label,
                'program_kode':       row['program_kode'],
                'program_nama':       row['program_nama'],
                'alamat_domisili':    row['alamat_domisili'],
                'provinsi_nama':      row['provinsi_nama'],
                'kabkota_nama':       row['kabkota_nama'],
                'kecamatan_nama':     row['kecamatan_nama'],
                'kelurahan_nama':     row['kelurahan_nama'],
                'ktp_alamat':         row['ktp_alamat'],
                'ktp_provinsi_nama':  row['ktp_provinsi_nama'],
                'ktp_kabkota_nama':   row['ktp_kabkota_nama'],
                'ktp_kecamatan_nama': row['ktp_kecamatan_nama'],
                'ktp_kelurahan_nama': row['ktp_kelurahan_nama'],
            })

        _apply_lag_dedup(items)
        return {'data': items}
