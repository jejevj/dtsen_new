from ..extensions import db
from datetime import datetime


class TUser(db.Model):
    """
    Model untuk tabel tuser (user internal SIMZAT).
    Kolom is_dtsen_user, is_soal_user, tipe_organisasi belum ada di DB production
    sehingga TIDAK didaftarkan di sini. Tambahkan saat kolom sudah di-ALTER.
    """
    __tablename__ = 'tuser'

    iduser        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id       = db.Column(db.String(40), nullable=True)
    user_fullname = db.Column(db.String(255), nullable=True)
    user_password = db.Column(db.String(32), nullable=True, comment='MD5')
    user_grup     = db.Column(db.String(100), nullable=True)
    list_office   = db.Column(db.String(255), nullable=True)
    approve       = db.Column(db.Integer, nullable=False, default=1)
    profpict      = db.Column(db.String(100), nullable=True)
    gender        = db.Column(db.Enum('M', 'F', 'O'), nullable=True)
    notelp        = db.Column(db.String(20), nullable=True)
    alamat        = db.Column(db.Text, nullable=True)
    email         = db.Column(db.String(255), nullable=True)
    remarks       = db.Column(db.Text, nullable=True)
    jabatan_nama  = db.Column(db.Text, nullable=True)
    jabatan_tmt   = db.Column(db.Date, nullable=True)
    golongan_abbr = db.Column(db.String(10), nullable=True)
    is_subscribe  = db.Column(db.String(1), nullable=True, default='N')
    created_at    = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, nullable=True)
    is_expired    = db.Column(db.String(1), nullable=True)

    # ---------------------------------------------------------------------------
    # Kolom ini ADA di skema tabel tapi belum di-ALTER ke DB production.
    # Uncomment saat sudah ditambahkan:
    # tipe_organisasi = db.Column(db.String(255), nullable=True)
    # is_soal_user    = db.Column(db.String(1), nullable=True, comment='flag Y, N, NULL')
    # is_dtsen_user   = db.Column(db.String(1), nullable=True, comment='flag Y, N, NULL')
    # ---------------------------------------------------------------------------

    @property
    def user_type(self):
        """Selalu 'tuser' — dipakai auth service untuk membedakan tipe user."""
        return 'tuser'

    def to_dict(self):
        return {
            'iduser':       self.iduser,
            'user_type':    self.user_type,
            'user_id':      self.user_id,
            'user_fullname':self.user_fullname,
            'user_grup':    self.user_grup,
            'list_office':  self.list_office,
            'approve':      self.approve,
            'profpict':     self.profpict,
            'gender':       self.gender,
            'notelp':       self.notelp,
            'alamat':       self.alamat,
            'email':        self.email,
            'remarks':      self.remarks,
            'jabatan_nama': self.jabatan_nama,
            'jabatan_tmt':  self.jabatan_tmt.isoformat() if self.jabatan_tmt else None,
            'golongan_abbr':self.golongan_abbr,
            'is_subscribe': self.is_subscribe,
            'created_at':   self.created_at.isoformat() if self.created_at else None,
            'updated_at':   self.updated_at.isoformat() if self.updated_at else None,
            'is_expired':   self.is_expired,
        }
