import hashlib
from datetime import date
from babel.dates import format_date
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


class MustahikService:
    @staticmethod
    def get_list(params: dict) -> dict:
        query = Mustahik.query

        if params.get('nama'):
            query = query.filter(Mustahik.nama_lengkap.ilike(f"%{params['nama']}%"))
        if params.get('nik'):
            query = query.filter_by(nik=int(params['nik']))
        if params.get('jenis_kelamin'):
            query = query.filter_by(jenis_kelamin=params['jenis_kelamin'])
        if params.get('agama'):
            query = query.filter_by(agama=params['agama'])
        if params.get('laz_kode'):
            query = query.filter_by(laz_kode=params['laz_kode'])
        if params.get('program_kode'):
            query = query.filter_by(program_kode=params['program_kode'])

        page = int(params.get('page', 1))
        per_page = int(params.get('per_page', 20))
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'data': mustahiks_schema.dump(paginated.items),
            'meta': {
                'page': paginated.page,
                'per_page': paginated.per_page,
                'total': paginated.total,
                'pages': paginated.pages,
            }
        }

    @staticmethod
    def get_detail(nik_hashed: str) -> dict:
        """
        Ambil detail mustahik berdasarkan MD5(nik).
        Setara getReallyDetaiMustahik di dtsen-sizawa:
        - JOIN wilayah domisili & KTP
        - JOIN LAZ (hanya aktif / daftar_ulang)
        - JOIN Program
        - Transformasi gender & format tanggal
        - Dedup field (nama, gender, agama, nik) antar baris LAZ yang sama
        """
        # Alias untuk join wilayah KTP
        KtpProvinsi = db.aliased(Provinsi, name='ktp_provinsi')
        KtpKabKota  = db.aliased(KabKota,  name='ktp_kabkota')
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
            .outerjoin(Provinsi,   Mustahik.provinsi_kode   == Provinsi.provinsi_kode)
            .outerjoin(KabKota,    Mustahik.kabkota_kode    == KabKota.kabkota_kode)
            .outerjoin(Kecamatan,  Mustahik.kecamatan_kode  == Kecamatan.kecamatan_kode)
            .outerjoin(Kelurahan,  Mustahik.kelurahan_kode  == Kelurahan.kelurahan_kode)
            .outerjoin(KtpProvinsi,  Mustahik.ktp_provinsi_kode  == KtpProvinsi.provinsi_kode)
            .outerjoin(KtpKabKota,   Mustahik.ktp_kabkota_kode   == KtpKabKota.kabkota_kode)
            .outerjoin(KtpKecamatan, Mustahik.ktp_kecamatan_kode == KtpKecamatan.kecamatan_kode)
            .outerjoin(KtpKelurahan, Mustahik.ktp_kelurahan_kode == KtpKelurahan.kelurahan_kode)
            .filter(
                db.func.md5(db.cast(Mustahik.nik, db.String)) == nik_hashed
            )
            .order_by(Mustahik.created_at.desc())
            .all()
        )

        if not rows:
            return {'message': 'Data tidak ditemukan.', 'status_code': 404}

        # --- Bangun list dict, lalu dedup seperti LAG di sizawa ---
        items = []
        for (
            m, laz_nama, skala, program_nama,
            provinsi_nama, kabkota_nama, kecamatan_nama, kelurahan_nama,
            ktp_provinsi_nama, ktp_kabkota_nama, ktp_kecamatan_nama, ktp_kelurahan_nama,
        ) in rows:
            items.append({
                'nik':               str(m.nik),
                'nik_hashed':        hashlib.md5(str(m.nik).encode()).hexdigest(),
                'kk':                m.kk,
                'nama_lengkap':      m.nama_lengkap,
                'jenis_kelamin':     GENDER_MAP.get(m.jenis_kelamin, m.jenis_kelamin),
                'lahir_tanggal':     _format_tanggal(m.lahir_tanggal),
                'agama':             m.agama,
                'rupiah':            str(m.rupiah),
                'tipe_penerimaan':   m.tipe_penerimaan,
                'tanggal_terima':    str(m.tanggal_terima) if m.tanggal_terima else None,
                'created_at':        str(m.created_at) if m.created_at else None,
                'laz_kode':          m.laz_kode,
                'laz_nama':          laz_nama,
                'skala':             SKALA_MAP.get(skala, str(skala)) if skala is not None else None,
                'program_kode':      m.program_kode,
                'program_nama':      program_nama,
                'alamat_domisili':   m.alamat_domisili,
                'provinsi_nama':     provinsi_nama,
                'kabkota_nama':      kabkota_nama,
                'kecamatan_nama':    kecamatan_nama,
                'kelurahan_nama':    kelurahan_nama,
                'ktp_alamat':        m.ktp_alamat,
                'ktp_provinsi_nama': ktp_provinsi_nama,
                'ktp_kabkota_nama':  ktp_kabkota_nama,
                'ktp_kecamatan_nama':ktp_kecamatan_nama,
                'ktp_kelurahan_nama':ktp_kelurahan_nama,
            })

        # --- Dedup: field yang sama antar baris berurutan → None (LAG logic) ---
        for i in range(1, len(items)):
            prev = items[i - 1]
            curr = items[i]

            if curr['nama_lengkap'] == prev['nama_lengkap']:
                curr['nama_lengkap'] = None
            # gender di-dedup hanya bila LAZ juga sama (persis seperti sizawa)
            if curr['jenis_kelamin'] == prev['jenis_kelamin'] and curr['laz_nama'] == prev['laz_nama']:
                curr['jenis_kelamin'] = None
            if curr['agama'] == prev['agama']:
                curr['agama'] = None
            if curr['nik'] == prev['nik']:
                curr['nik'] = None

        return {'data': mustahik_detail_schema.dump(items)}
