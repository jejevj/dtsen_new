import hashlib
from marshmallow import Schema, fields, validate


class MustahikSchema(Schema):
    """Schema ringkas untuk list mustahik."""
    id = fields.Int(dump_only=True)
    nik = fields.Int(load_only=True)
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

    def get_nik_hashed(self, obj):
        return hashlib.md5(str(obj.nik).encode()).hexdigest() if obj.nik else None


class MustahikDetailSchema(Schema):
    """
    Schema detail penerima — setara getReallyDetaiMustahik di dtsen-sizawa.
    Semua field join wilayah (domisili & KTP), LAZ, Program, beserta
    transformasi gender dan format tanggal sudah ditangani di service layer.
    """
    # Identitas
    nik = fields.String(allow_none=True)          # bisa None bila dedup
    nik_hashed = fields.String(allow_none=True)
    kk = fields.String(allow_none=True)
    nama_lengkap = fields.String(allow_none=True)  # bisa None bila dedup
    jenis_kelamin = fields.String(allow_none=True) # sudah ditransformasi: Laki-Laki / Perempuan
    lahir_tanggal = fields.String(allow_none=True) # format DD MMMM YYYY (string)
    agama = fields.String(allow_none=True)         # bisa None bila dedup

    # Penerimaan
    rupiah = fields.String(allow_none=True)        # as string agar tidak floating
    tipe_penerimaan = fields.String(allow_none=True)
    tanggal_terima = fields.String(allow_none=True)
    created_at = fields.String(allow_none=True)

    # LAZ
    laz_kode = fields.String(allow_none=True)
    laz_nama = fields.String(allow_none=True)
    skala = fields.String(allow_none=True)         # Nasional / Provinsi / Kabupaten/Kota

    # Program
    program_kode = fields.String(allow_none=True)
    program_nama = fields.String(allow_none=True)

    # Alamat Domisili
    alamat_domisili = fields.String(allow_none=True)
    provinsi_nama = fields.String(allow_none=True)
    kabkota_nama = fields.String(allow_none=True)
    kecamatan_nama = fields.String(allow_none=True)
    kelurahan_nama = fields.String(allow_none=True)

    # Alamat KTP
    ktp_alamat = fields.String(allow_none=True)
    ktp_provinsi_nama = fields.String(allow_none=True)
    ktp_kabkota_nama = fields.String(allow_none=True)
    ktp_kecamatan_nama = fields.String(allow_none=True)
    ktp_kelurahan_nama = fields.String(allow_none=True)
