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
    laz_kode               = db.Column(db.String(50), nullable=True, index=True)
    nip                    = db.Column(db.String(50), nullable=True)
    nik                    = db.Column(db.String(20), nullable=True, index=True)
    nama_lengkap           = db.Column(db.String(255), nullable=True)
    lahir_tanggal          = db.Column(db.Date, nullable=True)
    gender                 = db.Column(db.String(1), nullable=True)
    notelp                 = db.Column(db.String(50), nullable=True)
    email                  = db.Column(db.String(100), nullable=True)
    jabatan                = db.Column(db.String(255), nullable=True)
    instansi               = db.Column(db.String(255), nullable=True)
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
    akun_types             = db.Column(db.String(20), nullable=True,
                                       comment='laz,baznas,external,internal')
    catatan                = db.Column(db.Text, nullable=True)
    dtsen_akses_password   = db.Column(db.String(255), nullable=True, comment='MD5')
    deleted_at             = db.Column(db.DateTime, nullable=True)
    sent_at                = db.Column(db.DateTime, nullable=True)
    verified_at            = db.Column(db.DateTime, nullable=True)
    activated_at           = db.Column(db.DateTime, nullable=True)
    valid_from_at          = db.Column(db.Date, nullable=True, comment='Tanggal mulai akses aktif')
    valid_end_at           = db.Column(db.Date, nullable=True, comment='Tanggal berakhir akses')
    created_at             = db.Column(db.DateTime, nullable=True,
                                       server_default=db.func.current_timestamp())
    updated_at             = db.Column(db.DateTime, nullable=True)

    # Relasi ke wilayah dan dokumen
    wilayah = db.relationship('TDtsenWilayah', backref='akses', lazy='dynamic',
                              foreign_keys='TDtsenWilayah.dtsen_akses_id')
    dokumen = db.relationship('TDtsenDokumen', backref='akses_dokumen', lazy='dynamic',
                              foreign_keys='TDtsenDokumen.dtsen_akses_id')

    # Relasi ke Laz — join manual pakai non-FK karena laz_kode bukan FK DDL
    laz = db.relationship(
        'Laz',
        primaryjoin='foreign(TDtsenAkses.laz_kode) == Laz.laz_kode',
        lazy='joined',
        viewonly=True,
        uselist=False
    )

    @property
    def user_type(self):
        """Selalu 'dtsen' — dipakai auth service untuk membedakan tipe user."""
        return 'dtsen'

    @property
    def laz_skala(self) -> int | None:
        """
        Return skala LAZ yang dimiliki akun ini:
          1 = Nasional  -> bisa akses semua provinsi
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
            'nip':                    self.nip,
            'nik':                    self.nik,
            'nama_lengkap':           self.nama_lengkap,
            'lahir_tanggal':          self.lahir_tanggal.isoformat() if self.lahir_tanggal else None,
            'gender':                 self.gender,
            'notelp':                 self.notelp,
            'email':                  self.email,
            'jabatan':                self.jabatan,
            'instansi':               self.instansi,
            'berkas_surat_pengajuan': self.berkas_surat_pengajuan,
            'berkas_ktp':             self.berkas_ktp,
            'berkas_kak':             self.berkas_kak,
            'berkas_bast':            self.berkas_bast,
            'statuses':               self.statuses,
            'akun_types':             self.akun_types,
            'catatan':                self.catatan,
            'deleted_at':             self.deleted_at.isoformat() if self.deleted_at else None,
            'sent_at':                self.sent_at.isoformat() if self.sent_at else None,
            'verified_at':            self.verified_at.isoformat() if self.verified_at else None,
            'activated_at':           self.activated_at.isoformat() if self.activated_at else None,
            'valid_from_at':          self.valid_from_at.isoformat() if self.valid_from_at else None,
            'valid_end_at':           self.valid_end_at.isoformat() if self.valid_end_at else None,
            'created_at':             self.created_at.isoformat() if self.created_at else None,
            'updated_at':             self.updated_at.isoformat() if self.updated_at else None,
        }
