from ..extensions import db


class Provinsi(db.Model):
    __tablename__ = 'm_provinsi'
    provinsi_kode  = db.Column(db.String(2), primary_key=True)
    provinsi_nama  = db.Column(db.String(255), nullable=True)
    provinsi_aktif = db.Column(db.String(1), nullable=True, default='y')

    kabkota_list = db.relationship(
        'KabKota',
        foreign_keys='KabKota.provinsi_kode',
        backref='provinsi',
        lazy='dynamic'
    )


class KabKota(db.Model):
    __tablename__ = 'm_kabkota'
    kabkota_kode  = db.Column(db.String(4), primary_key=True)
    kabkota_nama  = db.Column(db.String(255), nullable=True)
    kabkota_aktif = db.Column(db.String(1), nullable=True, default='y')
    provinsi_kode = db.Column(db.String(2), db.ForeignKey('m_provinsi.provinsi_kode'), nullable=True)

    kecamatan_list = db.relationship(
        'Kecamatan',
        foreign_keys='Kecamatan.kabkota_kode',
        backref='kabkota',
        lazy='dynamic'
    )


class Kecamatan(db.Model):
    __tablename__ = 'm_kecamatan'
    kecamatan_kode  = db.Column(db.String(6), primary_key=True)
    kecamatan_nama  = db.Column(db.String(255), nullable=True)
    kecamatan_aktif = db.Column(db.String(1), nullable=True, default='y')
    kabkota_kode    = db.Column(db.String(4), db.ForeignKey('m_kabkota.kabkota_kode'), nullable=True)


class Kelurahan(db.Model):
    __tablename__ = 'm_kelurahan'
    kelurahan_kode  = db.Column(db.String(10), primary_key=True)
    kelurahan_nama  = db.Column(db.String(255), nullable=True)
    kecamatan_kode  = db.Column(db.String(6), db.ForeignKey('m_kecamatan.kecamatan_kode'), nullable=True)
