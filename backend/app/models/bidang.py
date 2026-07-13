from ..extensions import db
from datetime import datetime


class Bidang(db.Model):
    """
    Tabel: m_bidang
    Master data bidang/kategori program penyaluran zakat.
    Contoh bidang: Pendidikan, Kesehatan, Ekonomi, dll.
    Relasi: t_program -> m_bidang (via bidang_kode)
    """
    __tablename__ = 'm_bidang'

    bidang_kode  = db.Column(db.String(10),  primary_key=True)
    bidang_label = db.Column(db.String(255), nullable=True, default=None)  # label tampilan bidang
    bidang_nama  = db.Column(db.String(255), nullable=True, default=None)  # nama lengkap bidang

    created_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, nullable=True,  default=None, onupdate=datetime.utcnow)

    # --- Relationship ---
    programs = db.relationship(
        'Program', backref='bidang', lazy='dynamic',
        primaryjoin='Bidang.bidang_kode == Program.bidang_kode',
        foreign_keys='Program.bidang_kode'
    )

    def __repr__(self):
        return f'<Bidang {self.bidang_kode} - {self.bidang_label}>'
