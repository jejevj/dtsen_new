from ..extensions import db
from datetime import datetime


class MUker(db.Model):
    """
    Model untuk tabel m_uker.
    Menyimpan data unit kerja (BAZNAS / Kemenag).
    """
    __tablename__ = 'm_uker'

    uker_kode        = db.Column(db.String(255), primary_key=True)
    uker_nama        = db.Column(db.String(255), nullable=False)
    uker_parent      = db.Column(db.String(255), nullable=True,  default='0')
    eselon_kode      = db.Column(db.String(2),   nullable=True,  default='0')
    nama_jabatan     = db.Column(db.String(255), nullable=True)
    nip_pejabat      = db.Column(db.String(200), nullable=True)
    nama_pejabat     = db.Column(db.String(200), nullable=True)
    status_pejabat   = db.Column(db.String(200), nullable=True)
    tipe_pejabat     = db.Column(db.String(200), nullable=True)
    singkatan        = db.Column(db.String(100), nullable=True)
    alamat           = db.Column(db.String(1000),nullable=True)
    hirarki          = db.Column(db.Text,        nullable=True)
    hirarki_daerah   = db.Column(db.Text,        nullable=True)
    eselon_1         = db.Column(db.String(255), nullable=True)
    eselon_2         = db.Column(db.String(255), nullable=True)
    eselon_3         = db.Column(db.String(255), nullable=True)
    eselon_4         = db.Column(db.String(255), nullable=True)
    provinsi_kode    = db.Column(db.String(2),   nullable=True)
    kabkota_kode     = db.Column(db.String(4),   nullable=True)
    kecamatan_kode   = db.Column(db.String(7),   nullable=True)
    kelurahan_kode   = db.Column(db.String(10),  nullable=True)
    uker_status      = db.Column(db.String(1),   nullable=True)
    is_kemenag       = db.Column(db.String(1),   nullable=True,  default='1')
    created_at       = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime,    nullable=True)

    def __repr__(self):
        return f'<MUker {self.uker_kode} {self.uker_nama}>'

    def to_dict(self):
        return {
            'uker_kode':      self.uker_kode,
            'uker_nama':      self.uker_nama,
            'uker_parent':    self.uker_parent,
            'eselon_kode':    self.eselon_kode,
            'nama_jabatan':   self.nama_jabatan,
            'nip_pejabat':    self.nip_pejabat,
            'nama_pejabat':   self.nama_pejabat,
            'status_pejabat': self.status_pejabat,
            'tipe_pejabat':   self.tipe_pejabat,
            'singkatan':      self.singkatan,
            'alamat':         self.alamat,
            'hirarki':        self.hirarki,
            'hirarki_daerah': self.hirarki_daerah,
            'eselon_1':       self.eselon_1,
            'eselon_2':       self.eselon_2,
            'eselon_3':       self.eselon_3,
            'eselon_4':       self.eselon_4,
            'provinsi_kode':  self.provinsi_kode,
            'kabkota_kode':   self.kabkota_kode,
            'kecamatan_kode': self.kecamatan_kode,
            'kelurahan_kode': self.kelurahan_kode,
            'uker_status':    self.uker_status,
            'is_kemenag':     self.is_kemenag,
            'created_at':     self.created_at.isoformat() if self.created_at else None,
            'updated_at':     self.updated_at.isoformat() if self.updated_at else None,
        }
