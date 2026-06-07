from ..extensions import db


class Laz(db.Model):
    __tablename__ = 't_laz'

    laz_kode = db.Column(db.String(50), primary_key=True)
    laz_nama = db.Column(db.String(255), nullable=False)
    laz_parent_kode = db.Column(db.String(50), nullable=True)
    laz_status = db.Column(db.Enum('aktif', 'daftar_ulang', 'nonaktif'), default='aktif')
    skala = db.Column(db.SmallInteger, nullable=False)  # 1=Nasional, 2=Provinsi, 3=Kab/Kota
    provinsi_kode = db.Column(db.String(10), db.ForeignKey('m_provinsi.provinsi_kode'), nullable=True)

    mustahik = db.relationship('Mustahik', backref='laz', lazy='dynamic')

    def __repr__(self):
        return f'<Laz {self.laz_kode} - {self.laz_nama}>'
