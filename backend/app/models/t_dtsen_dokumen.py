from ..extensions import db
from datetime import datetime


class TDtsenDokumen(db.Model):
    """
    Model untuk tabel t_dtsen_dokumen.
    Menyimpan berkas/dokumen pendukung yang diunggah oleh akun DTSEN.
    """
    __tablename__ = 't_dtsen_dokumen'

    dtsen_dokumen_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dtsen_akses_id     = db.Column(
        db.Integer,
        db.ForeignKey('t_dtsen_akses.dtsen_akses_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    dtsen_dokumen_tmp  = db.Column(db.Text,        nullable=True)
    dtsen_dokumen_nama = db.Column(db.String(255), nullable=True)
    dtsen_dokumen_ext  = db.Column(db.String(255), nullable=True)
    dtsen_dokumen_size = db.Column(db.Integer,     nullable=True)
    created_at         = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at         = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'dtsen_dokumen_id':   self.dtsen_dokumen_id,
            'dtsen_akses_id':     self.dtsen_akses_id,
            'dtsen_dokumen_tmp':  self.dtsen_dokumen_tmp,
            'dtsen_dokumen_nama': self.dtsen_dokumen_nama,
            'dtsen_dokumen_ext':  self.dtsen_dokumen_ext,
            'dtsen_dokumen_size': self.dtsen_dokumen_size,
            'created_at':         self.created_at.isoformat() if self.created_at else None,
            'updated_at':         self.updated_at.isoformat() if self.updated_at else None,
        }
