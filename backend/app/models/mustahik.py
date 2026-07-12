from ..extensions import db
from datetime import datetime


class Mustahik(db.Model):
    __tablename__ = 't_mustahik'

    # PK sesuai struktur tabel DB — tidak ada kolom 'id'
    nik = db.Column(db.BigInteger, primary_key=True, nullable=False)
    kk = db.Column(db.String(20), nullable=True)
    nama_lengkap = db.Column(db.String(255), nullable=False)
    jenis_kelamin = db.Column(db.Enum('m', 'f'), nullable=False)
    lahir_tanggal = db.Column(db.Date, nullable=True)
    agama = db.Column(db.String(50), nullable=True)

    # LAZ & Program
    laz_kode = db.Column(db.String(50), db.ForeignKey('t_laz.laz_kode'), nullable=False)
    program_kode = db.Column(db.String(50), db.ForeignKey('t_program.program_kode'), nullable=False)
    tipe_penerimaan = db.Column(db.Enum('pml', 'pmtl'), nullable=False)
    rupiah = db.Column(db.Numeric(15, 2), nullable=False)
    tanggal_terima = db.Column(db.Date, nullable=True)

    # Alamat Domisili
    alamat_domisili = db.Column(db.Text, nullable=True)
    provinsi_kode = db.Column(db.String(10), db.ForeignKey('m_provinsi.provinsi_kode'), nullable=True)
    kabkota_kode = db.Column(db.String(10), db.ForeignKey('m_kabkota.kabkota_kode'), nullable=True)
    kecamatan_kode = db.Column(db.String(10), db.ForeignKey('m_kecamatan.kecamatan_kode'), nullable=True)
    kelurahan_kode = db.Column(db.String(10), db.ForeignKey('m_kelurahan.kelurahan_kode'), nullable=True)

    # Alamat KTP
    ktp_alamat = db.Column(db.Text, nullable=True)
    ktp_provinsi_kode = db.Column(db.String(10), db.ForeignKey('m_provinsi.provinsi_kode'), nullable=True)
    ktp_kabkota_kode = db.Column(db.String(10), db.ForeignKey('m_kabkota.kabkota_kode'), nullable=True)
    ktp_kecamatan_kode = db.Column(db.String(10), db.ForeignKey('m_kecamatan.kecamatan_kode'), nullable=True)
    ktp_kelurahan_kode = db.Column(db.String(10), db.ForeignKey('m_kelurahan.kelurahan_kode'), nullable=True)
    ktp_berkas = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Relationships ---
    program = db.relationship('Program', backref='mustahik_list', lazy='joined', foreign_keys=[program_kode])

    provinsi = db.relationship(
        'Provinsi', backref='mustahik_domisili', lazy='joined',
        primaryjoin='Mustahik.provinsi_kode == Provinsi.provinsi_kode', foreign_keys=[provinsi_kode]
    )
    kabkota = db.relationship(
        'KabKota', backref='mustahik_domisili', lazy='joined',
        primaryjoin='Mustahik.kabkota_kode == KabKota.kabkota_kode', foreign_keys=[kabkota_kode]
    )
    kecamatan = db.relationship(
        'Kecamatan', backref='mustahik_domisili', lazy='joined',
        primaryjoin='Mustahik.kecamatan_kode == Kecamatan.kecamatan_kode', foreign_keys=[kecamatan_kode]
    )
    kelurahan = db.relationship(
        'Kelurahan', backref='mustahik_domisili', lazy='joined',
        primaryjoin='Mustahik.kelurahan_kode == Kelurahan.kelurahan_kode', foreign_keys=[kelurahan_kode]
    )

    ktp_provinsi = db.relationship(
        'Provinsi', backref='mustahik_ktp', lazy='joined',
        primaryjoin='Mustahik.ktp_provinsi_kode == Provinsi.provinsi_kode', foreign_keys=[ktp_provinsi_kode]
    )
    ktp_kabkota = db.relationship(
        'KabKota', backref='mustahik_ktp', lazy='joined',
        primaryjoin='Mustahik.ktp_kabkota_kode == KabKota.kabkota_kode', foreign_keys=[ktp_kabkota_kode]
    )
    ktp_kecamatan = db.relationship(
        'Kecamatan', backref='mustahik_ktp', lazy='joined',
        primaryjoin='Mustahik.ktp_kecamatan_kode == Kecamatan.kecamatan_kode', foreign_keys=[ktp_kecamatan_kode]
    )
    ktp_kelurahan = db.relationship(
        'Kelurahan', backref='mustahik_ktp', lazy='joined',
        primaryjoin='Mustahik.ktp_kelurahan_kode == Kelurahan.kelurahan_kode', foreign_keys=[ktp_kelurahan_kode]
    )

    def __repr__(self):
        return f'<Mustahik {self.nik} - {self.nama_lengkap}>'
