from ..extensions import db
from datetime import datetime


class TUser(db.Model):
    __tablename__ = 'tuser'

    iduser       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username     = db.Column(db.String(100), nullable=True)
    password     = db.Column(db.String(255), nullable=True, comment='MD5 atau hash')
    nama_lengkap = db.Column(db.String(255), nullable=True)
    email        = db.Column(db.String(255), nullable=True)
    nohp         = db.Column(db.String(50), nullable=True)
    laz_kode     = db.Column(db.String(50), nullable=True)
    uker_kode    = db.Column(db.String(255), nullable=True)
    role         = db.Column(db.String(50), nullable=True)
    statuses     = db.Column(db.String(20), nullable=True, default='aktif')
    last_login   = db.Column(db.DateTime, nullable=True)
    created_at   = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'iduser':       self.iduser,
            'username':     self.username,
            'nama_lengkap': self.nama_lengkap,
            'email':        self.email,
            'nohp':         self.nohp,
            'laz_kode':     self.laz_kode,
            'uker_kode':    self.uker_kode,
            'role':         self.role,
            'statuses':     self.statuses,
            'last_login':   self.last_login.isoformat() if self.last_login else None,
            'created_at':   self.created_at.isoformat() if self.created_at else None,
            'updated_at':   self.updated_at.isoformat() if self.updated_at else None,
        }
