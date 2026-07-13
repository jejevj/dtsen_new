from ..extensions import db
from datetime import datetime


class Penerimaan(db.Model):
    """
    Tabel: t_penerimaan
    Nominal penerimaan (pengumpulan zakat) per LAZ per tahun.
    Digunakan di HomeModel.getAgregatPenerimaan() untuk agregasi peta provinsi.
    """
    __tablename__ = 't_penerimaan'

    penerimaan_id     = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    laz_kode          = db.Column(db.String(255), db.ForeignKey('t_laz.laz_kode'), nullable=False, index=True)
    penerimaan_nominal = db.Column(db.BigInteger, nullable=True, default=None)  # nominal zakat yang diterima
    penerimaan_tahun  = db.Column(db.SmallInteger, nullable=True, default=None)  # tahun (e.g. 2023, 2024)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True,  default=None, onupdate=datetime.utcnow)

    # --- Relationship ---
    laz = db.relationship(
        'Laz', backref='penerimaan_list', lazy='joined',
        foreign_keys=[laz_kode]
    )

    def __repr__(self):
        return f'<Penerimaan laz={self.laz_kode} tahun={self.penerimaan_tahun} nominal={self.penerimaan_nominal}>'
