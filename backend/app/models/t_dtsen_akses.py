from ..extensions import db
from datetime import datetime


class TDtsenAkses(db.Model):
    """
    Model untuk tabel t_dtsen_akses (user eksternal DTSEN / LAZ).
    Referensi ke t_laz melalui laz_kode untuk menentukan skala akses:
      - skala 1 (Nasional)  : drilldown provinsi -> kabkota -> kecamatan
      - skala 2 (Provinsi)  : drilldown kabkota yang di-assign
      - skala 3 (Kab/Kota)  : drilldown kecamatan saja
    """
    __tablename__ = 't_dtsen_akses'

    dtsen_akses_id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    laz_kode               = db.Column(db.String(50), db.ForeignKey('t_laz.laz_kode'),
                                       nullable=True, index=True)
    nik                    = db.Column(db.String(20), nullable=True, index=True)
    nama_lengkap           = db.Column(db.String(255), nullable=True)
    lahir_tanggal          = db.Column(db.Date, nullable=True)
    gender                 = db.Column(db.String(1), nullable=True)
    notelp                 = db.Column(db.String(50), nullable=True)
    email                  = db.Column(db.String(100), nullable=True)
    jabatan                = db.Column(db.String(255), nullable=True)
    berkas_surat_pengajuan = db.Column(db.String(255), nullable=True)
    berkas_ktp             = db.Column(db.String(255), nullable=True)
    berkas_kak             = db.Column(db.String(255), nullable=True)
    berkas_bast            = db.Column(db.String(255), nullable=True)
    statuses               = db.Column(
        db.Enum(
            'draf', 'pengajuan', 'disetujui', 'dikembalikan',
            'revisi', 'finalisasi', 'aktif', 'inaktif'
        ),
        nullable=True,
        default='draf',
        index=True
    )
    catatan                = db.Column(db.Text, nullable=True)
    dtsen_akses_password   = db.Column(db.String(255), nullable=True, comment='MD5')
    deleted_at             = db.Column(db.DateTime, nullable=True)
    sent_at                = db.Column(db.DateTime, nullable=True)
    activated_at           = db.Column(db.DateTime, nullable=True)
    created_at             = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at             = db.Column(db.DateTime, nullable=True)

    # Relasi ke wilayah dan dokumen
    wilayah   = db.relationship('TDtsenWilayah', backref='akses', lazy='dynamic',
                                foreign_keys='TDtsenWilayah.dtsen_akses_id')
    dokumen   = db.relationship('TDtsenDokumen', backref='akses', lazy='dynamic',
                                foreign_keys='TDtsenDokumen.dtsen_akses_id')

    # Relasi ke t_laz untuk membaca skala
    laz = db.relationship('Laz', foreign_keys=[laz_kode],
                          primaryjoin='TDtsenAkses.laz_kode == foreign(Laz.laz_kode)',
                          backref='akses_users', lazy='joined', viewonly=True)

    @property
    def user_type(self):
        """Selalu 'dtsen' — dipakai auth service untuk membedakan tipe user."""
        return 'dtsen'

    @property
    def laz_skala(self) -> int | None:
        """
        Return skala LAZ yang dimiliki akun ini:
          1 = Nasional  -> bisa akses semua provinsi (berdasar t_dtsen_wilayah)
          2 = Provinsi  -> bisa akses kabkota yang di-assign
          3 = Kab/Kota  -> bisa akses kecamatan saja
        Return None jika LAZ tidak ditemukan.
        """
        return self.laz.skala if self.laz else None

    def to_dict(self):
        return {
            'dtsen_akses_id':         self.dtsen_akses_id,
            'user_type':              self.user_type,
            'laz_kode':               self.laz_kode,
            'laz_skala':              self.laz_skala,
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
