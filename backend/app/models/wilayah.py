from ..extensions import db


class Provinsi(db.Model):
    __tablename__ = 'm_provinsi'
    provinsi_kode = db.Column(db.String(10), primary_key=True)
    provinsi_nama = db.Column(db.String(100), nullable=False)

    # Relasi ke kab/kota yang berada di provinsi ini
    kabkota_list = db.relationship(
        'KabKota',
        foreign_keys='KabKota.provinsi_kode',
        backref='provinsi',
        lazy='dynamic'
    )


class KabKota(db.Model):
    __tablename__ = 'm_kabkota'
    kabkota_kode  = db.Column(db.String(10), primary_key=True)
    kabkota_nama  = db.Column(db.String(100), nullable=False)
    # Setiap kab/kota harus diketahui induk provinsinya
    provinsi_kode = db.Column(db.String(10), db.ForeignKey('m_provinsi.provinsi_kode'), nullable=True)

    kecamatan_list = db.relationship(
        'Kecamatan',
        foreign_keys='Kecamatan.kabkota_kode',
        backref='kabkota',
        lazy='dynamic'
    )


class Kecamatan(db.Model):
    __tablename__ = 'm_kecamatan'
    kecamatan_kode = db.Column(db.String(10), primary_key=True)
    kecamatan_nama = db.Column(db.String(100), nullable=False)
    kabkota_kode   = db.Column(db.String(10), db.ForeignKey('m_kabkota.kabkota_kode'), nullable=True)

    kelurahan_list = db.relationship(
        'Kelurahan',
        foreign_keys='Kelurahan.kecamatan_kode',
        backref='kecamatan',
        lazy='dynamic'
    )


class Kelurahan(db.Model):
    __tablename__ = 'm_kelurahan'
    kelurahan_kode = db.Column(db.String(10), primary_key=True)
    kelurahan_nama = db.Column(db.String(100), nullable=False)
    kecamatan_kode = db.Column(db.String(10), db.ForeignKey('m_kecamatan.kecamatan_kode'), nullable=True)
