from marshmallow import Schema, fields, validate


class MustahikSchema(Schema):
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
        import hashlib
        return hashlib.md5(str(obj.nik).encode()).hexdigest() if obj.nik else None
