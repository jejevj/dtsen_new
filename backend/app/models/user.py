from ..extensions import db
from datetime import datetime


# Tabel pivot: relasi User <-> Wilayah berdasarkan level role
class UserWilayah(db.Model):
    """
    Tabel assignment wilayah per user.
    - pj_nasional : provinsi_kode diisi, kabkota_kode NULL
    - pj_provinsi : provinsi_kode diisi, kabkota_kode diisi
    - pj_kabkota  : provinsi_kode diisi, kabkota_kode diisi (satu record)
    """
    __tablename__ = 'user_wilayah'

    id             = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id        = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    provinsi_kode  = db.Column(db.String(10), db.ForeignKey('m_provinsi.provinsi_kode'), nullable=True)
    kabkota_kode   = db.Column(db.String(10), db.ForeignKey('m_kabkota.kabkota_kode'),   nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user     = db.relationship('User',     back_populates='wilayah_assignments')
    provinsi = db.relationship('Provinsi', foreign_keys=[provinsi_kode], lazy='joined')
    kabkota  = db.relationship('KabKota',  foreign_keys=[kabkota_kode],  lazy='joined')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'provinsi_kode', 'kabkota_kode', name='uq_user_wilayah'),
    )

    def __repr__(self):
        return f'<UserWilayah user_id={self.user_id} prov={self.provinsi_kode} kab={self.kabkota_kode}>'


class User(db.Model):
    """
    Role yang valid:
      - pj_nasional  : Penanggung Jawab Nasional
                       Dapat melihat laporan 10 provinsi yang di-assign.
                       Dapat memeriksa semua NIK (pemeriksaan dtsen).
      - pj_provinsi  : Penanggung Jawab Provinsi
                       Dapat melihat laporan 4 kab/kota di provinsinya.
                       Dapat memeriksa semua NIK.
      - pj_kabkota   : Penanggung Jawab Kab/Kota
                       Hanya melihat data di kab/kota tempat dia berizin.
                       Dapat memeriksa semua NIK.
      - admin        : Super admin, akses penuh.
    """
    __tablename__ = 'users'

    id                = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name              = db.Column(db.String(255), nullable=False)
    username          = db.Column(db.String(100), unique=True, nullable=True)
    nip               = db.Column(db.String(30),  unique=True, nullable=True)
    email             = db.Column(db.String(255), unique=True, nullable=False)

    # Role: admin | pj_nasional | pj_provinsi | pj_kabkota
    role              = db.Column(db.String(50),  nullable=False, default='pj_kabkota')

    password          = db.Column(db.String(255), nullable=False)
    email_verified_at = db.Column(db.DateTime,    nullable=True)
    remember_token    = db.Column(db.String(100), nullable=True)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at        = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi ke tabel assignment wilayah
    wilayah_assignments = db.relationship(
        'UserWilayah',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    # ------------------------------------------------------------------ helpers
    @property
    def provinsi_codes(self):
        """Daftar kode provinsi yang di-assign ke user ini."""
        return [
            w.provinsi_kode
            for w in self.wilayah_assignments
            if w.provinsi_kode is not None
        ]

    @property
    def kabkota_codes(self):
        """Daftar kode kab/kota yang di-assign ke user ini."""
        return [
            w.kabkota_kode
            for w in self.wilayah_assignments
            if w.kabkota_kode is not None
        ]

    def can_access_provinsi(self, provinsi_kode):
        """Cek apakah user boleh mengakses data provinsi tertentu."""
        if self.role == 'admin':
            return True
        return provinsi_kode in self.provinsi_codes

    def can_access_kabkota(self, kabkota_kode):
        """Cek apakah user boleh mengakses data kab/kota tertentu."""
        if self.role == 'admin':
            return True
        if self.role == 'pj_nasional':
            # Nasional hanya difilter ke provinsi, bukan per kab/kota
            return True
        return kabkota_kode in self.kabkota_codes

    def __repr__(self):
        return f'<User {self.email} [{self.role}]>'
