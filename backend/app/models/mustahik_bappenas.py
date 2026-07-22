from ..extensions import db
from datetime import datetime


class MustahikBappenas(db.Model):
    """
    Tabel: t_mustahik_bappenas
    Data desil kemiskinan mustahik dari integrasi Bappenas.
    Digunakan sebagai lookup desil (0-10) berdasarkan NIK.
    """
    __tablename__ = 't_mustahik_bappenas'

    id         = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nik        = db.Column(db.String(16), db.ForeignKey('t_mustahik.nik'), nullable=False, index=True)
    desil      = db.Column(db.SmallInteger, nullable=True, default=None)  # nilai 1-10, NULL jika tidak ada data

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True,  default=None, onupdate=datetime.utcnow)

    # --- Relationship ---
    mustahik = db.relationship(
        'Mustahik', backref='bappenas_data', lazy='joined',
        foreign_keys=[nik],
        primaryjoin='MustahikBappenas.nik == Mustahik.nik'
    )

    def __repr__(self):
        return f'<MustahikBappenas nik={self.nik} desil={self.desil}>'
