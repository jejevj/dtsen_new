from ..extensions import db
from datetime import datetime
from .mustahik_bappenas import MustahikBappenas


class Mustahik(db.Model):
    __tablename__ = 't_mustahik'

    mustahik_id     = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    laz_kode        = db.Column(db.String(255), db.ForeignKey('t_laz.laz_kode'), nullable=False)
    program_kode    = db.Column(db.String(10),  db.ForeignKey('t_program.program_kode'), nullable=False)
    tanggal_terima  = db.Column(db.Date, nullable=False)
    tipe_penerimaan = db.Column(db.String(10),  nullable=True,  default=None)
    rupiah          = db.Column(db.Integer,      nullable=False)

    # Identitas
    nik             = db.Column(db.String(16),  nullable=True,  default=None)
    kk              = db.Column(db.String(20),  nullable=True,  default=None)
    nama_lengkap    = db.Column(db.String(255), nullable=True,  default=None)
    jenis_kelamin   = db.Column(db.String(1),   nullable=False, default='m')
    lahir_tanggal   = db.Column(db.Date,        nullable=True,  default=None)
    agama           = db.Column(db.String(255), nullable=True,  default=None)
    kawin_status    = db.Column(db.String(2),   nullable=True,  default='kw')
    tanggungan      = db.Column(db.Integer,     nullable=True,  default=None)
    keterangan      = db.Column(db.Text,        nullable=True,  default=None)

    # Alamat Domisili
    is_same_alamat  = db.Column(db.String(1),   nullable=True,  default=None)
    alamat_domisili = db.Column(db.Text,        nullable=True,  default=None)
    provinsi_kode   = db.Column(db.String(2),   db.ForeignKey('m_provinsi.provinsi_kode'),   nullable=True)
    kabkota_kode    = db.Column(db.String(4),   db.ForeignKey('m_kabkota.kabkota_kode'),     nullable=True)
    kecamatan_kode  = db.Column(db.String(6),   db.ForeignKey('m_kecamatan.kecamatan_kode'), nullable=True)
    kelurahan_kode  = db.Column(db.String(10),  db.ForeignKey('m_kelurahan.kelurahan_kode'), nullable=True)

    # Alamat KTP
    ktp_alamat         = db.Column(db.String(255), nullable=True, default=None)
    ktp_provinsi_kode  = db.Column(db.String(2),   db.ForeignKey('m_provinsi.provinsi_kode'),   nullable=True)
    ktp_kabkota_kode   = db.Column(db.String(4),   db.ForeignKey('m_kabkota.kabkota_kode'),     nullable=True)
    ktp_kecamatan_kode = db.Column(db.String(6),   db.ForeignKey('m_kecamatan.kecamatan_kode'), nullable=True)
    ktp_kelurahan_kode = db.Column(db.String(10),  db.ForeignKey('m_kelurahan.kelurahan_kode'), nullable=True)
    ktp_berkas         = db.Column(db.Text,        nullable=True, default=None)  # longtext
    ktp_berkas_type    = db.Column(db.String(255), nullable=True, default=None)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True,  default=None, onupdate=datetime.utcnow)

    # --- Relationships ---
    program = db.relationship(
        'Program', backref='mustahik_list', lazy='joined', foreign_keys=[program_kode]
    )
    provinsi = db.relationship(
        'Provinsi', backref='mustahik_domisili', lazy='joined',
        primaryjoin='Mustahik.provinsi_kode == Provinsi.provinsi_kode',
        foreign_keys=[provinsi_kode]
    )
    kabkota = db.relationship(
        'KabKota', backref='mustahik_domisili', lazy='joined',
        primaryjoin='Mustahik.kabkota_kode == KabKota.kabkota_kode',
        foreign_keys=[kabkota_kode]
    )
    kecamatan = db.relationship(
        'Kecamatan', backref='mustahik_domisili', lazy='joined',
        primaryjoin='Mustahik.kecamatan_kode == Kecamatan.kecamatan_kode',
        foreign_keys=[kecamatan_kode]
    )
    kelurahan = db.relationship(
        'Kelurahan', backref='mustahik_domisili', lazy='joined',
        primaryjoin='Mustahik.kelurahan_kode == Kelurahan.kelurahan_kode',
        foreign_keys=[kelurahan_kode]
    )
    ktp_provinsi = db.relationship(
        'Provinsi', backref='mustahik_ktp', lazy='joined',
        primaryjoin='Mustahik.ktp_provinsi_kode == Provinsi.provinsi_kode',
        foreign_keys=[ktp_provinsi_kode]
    )
    ktp_kabkota = db.relationship(
        'KabKota', backref='mustahik_ktp', lazy='joined',
        primaryjoin='Mustahik.ktp_kabkota_kode == KabKota.kabkota_kode',
        foreign_keys=[ktp_kabkota_kode]
    )
    ktp_kecamatan = db.relationship(
        'Kecamatan', backref='mustahik_ktp', lazy='joined',
        primaryjoin='Mustahik.ktp_kecamatan_kode == Kecamatan.kecamatan_kode',
        foreign_keys=[ktp_kecamatan_kode]
    )
    ktp_kelurahan = db.relationship(
        'Kelurahan', backref='mustahik_ktp', lazy='joined',
        primaryjoin='Mustahik.ktp_kelurahan_kode == Kelurahan.kelurahan_kode',
        foreign_keys=[ktp_kelurahan_kode]
    )
    bappenas = db.relationship(
        "MustahikBappenas",
        lazy="joined",
        uselist=False,
        primaryjoin="foreign(Mustahik.nik) == MustahikBappenas.nik"
    )

    def __repr__(self):
        return f'<Mustahik {self.mustahik_id} - {self.nama_lengkap}>'
