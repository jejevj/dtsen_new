import hashlib
import base64
from marshmallow import Schema, fields, validate
from datetime import date, datetime

class MustahikSchema(Schema):
    """Schema ringkas untuk list mustahik."""
    # id dihapus — PK tabel adalah nik
    nik = fields.Method("get_masked_nik", dump_only=True)
    nik_hashed = fields.Method('get_nik_hashed', dump_only=True)
    kk = fields.Str(allow_none=True)
    nama_lengkap = fields.Str(required=True)
    jenis_kelamin = fields.Str(required=True, validate=validate.OneOf(['m', 'f']))
    lahir_tanggal = fields.Date(allow_none=True)
    agama = fields.Str(allow_none=True)
    laz_kode = fields.Str(required=True)
    program_kode = fields.Str(required=True)
    tipe_penerimaan = fields.Str(required=True, validate=validate.OneOf(['pml', 'pmtl']))
    rupiah = fields.Decimal(required=True, as_string=True)
    tanggal_terima = fields.Date(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    usia = fields.Method("_hitung_usia", dump_only=True)

    # Wilayah domisili (dari relationship lazy='joined')
    kabkota_nama = fields.Method('get_kabkota_nama', dump_only=True)
    provinsi_nama = fields.Method('get_provinsi_nama', dump_only=True)
    desil = fields.Method("get_desil", dump_only=True)

    # def get_nik_hashed(self, obj):
    #     return hashlib.md5(str(obj.nik).encode()).hexdigest() if obj.nik else None

    def get_nik_hashed(self, obj):
        if not obj.nik:
            return None
        return base64.urlsafe_b64encode(str(obj.nik).encode()).decode()

    def get_kabkota_nama(self, obj):
        return obj.ktp_kabkota.kabkota_nama if obj.ktp_kabkota else None

    def get_provinsi_nama(self, obj):
        return obj.ktp_provinsi.provinsi_nama if obj.ktp_provinsi else None

    def get_desil(self, obj):
        return obj.bappenas.desil if obj.bappenas else None

    def get_masked_nik(self, obj):
        if not obj.nik:
            return None

        nik = str(obj.nik)

        if len(nik) <= 7:
            return nik

        return f"{nik[:6]}{'*' * (len(nik) - 7)}{nik[-1]}"

    def _hitung_usia(self, obj):
        if not obj.lahir_tanggal:
            return None

        tanggal = obj.lahir_tanggal

        if isinstance(tanggal, str):
            try:
                tanggal = datetime.strptime(tanggal, "%Y-%m-%d").date()
            except ValueError:
                return None

        hari_ini = date.today()
        usia = hari_ini.year - tanggal.year

        if (hari_ini.month, hari_ini.day) < (tanggal.month, tanggal.day):
            usia -= 1

        return usia


class MustahikDetailSchema(Schema):
    """
    Schema detail penerima — setara getReallyDetaiMustahik di dtsen-sizawa.
    """
    nik = fields.String(allow_none=True)
    nik_hashed = fields.String(allow_none=True)
    kk = fields.String(allow_none=True)
    nama_lengkap = fields.String(allow_none=True)
    jenis_kelamin = fields.String(allow_none=True)
    lahir_tanggal = fields.String(allow_none=True)
    agama = fields.String(allow_none=True)

    rupiah = fields.String(allow_none=True)
    tipe_penerimaan = fields.String(allow_none=True)
    tanggal_terima = fields.String(allow_none=True)
    created_at = fields.String(allow_none=True)

    laz_kode = fields.String(allow_none=True)
    laz_nama = fields.String(allow_none=True)
    skala = fields.String(allow_none=True)

    program_kode = fields.String(allow_none=True)
    program_nama = fields.String(allow_none=True)

    alamat_domisili = fields.String(allow_none=True)
    provinsi_nama = fields.String(allow_none=True)
    kabkota_nama = fields.String(allow_none=True)
    kecamatan_nama = fields.String(allow_none=True)
    kelurahan_nama = fields.String(allow_none=True)

    ktp_alamat = fields.String(allow_none=True)
    ktp_provinsi_nama = fields.String(allow_none=True)
    ktp_kabkota_nama = fields.String(allow_none=True)
    ktp_kecamatan_nama = fields.String(allow_none=True)
    ktp_kelurahan_nama = fields.String(allow_none=True)
