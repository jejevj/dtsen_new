from ..extensions import db
from datetime import datetime
import enum


class StatusesEnum(enum.Enum):
    draf         = 'draf'
    pengajuan    = 'pengajuan'
    disetujui    = 'disetujui'
    dikembalikan = 'dikembalikan'
    revisi       = 'revisi'
    finalisasi   = 'finalisasi'
    aktif        = 'aktif'
    inaktif      = 'inaktif'


class TDtsenAkses(db.Model):
    __tablename__ = 't_dtsen_akses'

    dtsen_akses_id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    laz_kode                = db.Column(db.String(50), nullable=True, index=True)
    nik                     = db.Column(db.String(20), nullable=True, index=True)
    nama_lengkap            = db.Column(db.String(255), nullable=True)
    lahir_tanggal           = db.Column(db.Date, nullable=True)
    gender                  = db.Column(db.String(1), nullable=True)
    notelp                  = db.Column(db.String(50), nullable=True)
    email                   = db.Column(db.String(100), nullable=True)
    jabatan                 = db.Column(db.String(255), nullable=True)
    berkas_surat_pengajuan  = db.Column(db.String(255), nullable=True)
    berkas_ktp              = db.Column(db.String(255), nullable=True)
    berkas_kak              = db.Column(db.String(255), nullable=True)
    berkas_bast             = db.Column(db.String(255), nullable=True)
    statuses                = db.Column(
        db.Enum('draf', 'pengajuan', 'disetujui', 'dikembalikan', 'revisi', 'finalisasi', 'aktif', 'inaktif'),
        nullable=True,
        default='draf',
        index=True
    )
    catatan                 = db.Column(db.Text, nullable=True)
    dtsen_akses_password    = db.Column(db.String(255), nullable=True, comment='MD5')
    deleted_at              = db.Column(db.DateTime, nullable=True)
    sent_at                 = db.Column(db.DateTime, nullable=True)
    activated_at            = db.Column(db.DateTime, nullable=True)
    created_at              = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at              = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'dtsen_akses_id':         self.dtsen_akses_id,
            'laz_kode':               self.laz_kode,
            'nik':                    self.nik,
            'nama_lengkap':           self.nama_lengkap,
            'lahir_tanggal':          self.lahir_tanggal.isoformat() if self.lahir_tanggal else None,
            'gender':                 self.gender,
            'notelp':                 self.notelp,
            'email':                  self.email,
            'jabatan':                self.jabatan,
            'berkas_surat_pengajuan': self.berkas_surat_pengajuan,
            'berkas_ktp':             self.berkas_ktp,
            'berkas_kak':             self.berkas_kak,
            'berkas_bast':            self.berkas_bast,
            'statuses':               self.statuses,
            'catatan':                self.catatan,
            'deleted_at':             self.deleted_at.isoformat() if self.deleted_at else None,
            'sent_at':                self.sent_at.isoformat() if self.sent_at else None,
            'activated_at':           self.activated_at.isoformat() if self.activated_at else None,
            'created_at':             self.created_at.isoformat() if self.created_at else None,
            'updated_at':             self.updated_at.isoformat() if self.updated_at else None,
        }
