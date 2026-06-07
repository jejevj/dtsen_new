from ..extensions import db


class Provinsi(db.Model):
    __tablename__ = 'm_provinsi'
    provinsi_kode = db.Column(db.String(10), primary_key=True)
    provinsi_nama = db.Column(db.String(100), nullable=False)


class KabKota(db.Model):
    __tablename__ = 'm_kabkota'
    kabkota_kode = db.Column(db.String(10), primary_key=True)
    kabkota_nama = db.Column(db.String(100), nullable=False)


class Kecamatan(db.Model):
    __tablename__ = 'm_kecamatan'
    kecamatan_kode = db.Column(db.String(10), primary_key=True)
    kecamatan_nama = db.Column(db.String(100), nullable=False)


class Kelurahan(db.Model):
    __tablename__ = 'm_kelurahan'
    kelurahan_kode = db.Column(db.String(10), primary_key=True)
    kelurahan_nama = db.Column(db.String(100), nullable=False)
