from ..extensions import db
from datetime import datetime


class TDtsenWilayah(db.Model):
    """
    Model untuk tabel t_dtsen_wilayah.
    Menyimpan cakupan wilayah kerja tiap akun DTSEN (LAZ).
    Satu akun bisa memiliki lebih dari satu baris wilayah.
    """
    __tablename__ = 't_dtsen_wilayah'

    # Composite primary key — tidak ada PK tunggal pada skema ini
    __table_args__ = (
        db.PrimaryKeyConstraint('dtsen_akses_id', 'provinsi_kode', 'kabkota_kode', 'kecamatan_kode'),
    )

    dtsen_akses_id   = db.Column(
        db.Integer,
        db.ForeignKey('t_dtsen_akses.dtsen_akses_id', ondelete='CASCADE'),
        nullable=False
    )
    provinsi_kode    = db.Column(db.String(2),  nullable=True)
    kabkota_kode     = db.Column(db.String(4),  nullable=True)
    kecamatan_kode   = db.Column(db.String(6),  nullable=True)
    created_at       = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'dtsen_akses_id':  self.dtsen_akses_id,
            'provinsi_kode':   self.provinsi_kode,
            'kabkota_kode':    self.kabkota_kode,
            'kecamatan_kode':  self.kecamatan_kode,
            'created_at':      self.created_at.isoformat() if self.created_at else None,
            'updated_at':      self.updated_at.isoformat() if self.updated_at else None,
        }
