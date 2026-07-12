from ..extensions import db
from datetime import datetime
from sqlalchemy import Index, BigInteger, String, Text, Date, DateTime, Integer, JSON


class ZawaAnggota(db.Model):
    """
    Tabel lokal cache data anggota ZAWA dari API Kemenag.
    Di-sync via POST /api/v1/baseline/sync.
    Index di nik & nama untuk pencarian cepat.
    """
    __tablename__ = 'zawa_anggota'

    id                       = db.Column(BigInteger, primary_key=True, autoincrement=True)

    # Identitas utama — wajib ada index karena sering di-search
    nomor_induk_kependudukan = db.Column(String(16),  nullable=True, default=None, index=True)
    nomor_kartu_keluarga     = db.Column(String(16),  nullable=True, default=None, index=True)
    nama                     = db.Column(String(255), nullable=True, default=None)
    jenis_kelamin            = db.Column(String(10),  nullable=True, default=None)
    tanggal_lahir            = db.Column(Date,        nullable=True, default=None)
    tempat_lahir             = db.Column(String(100), nullable=True, default=None)
    agama                    = db.Column(String(50),  nullable=True, default=None)
    status_perkawinan        = db.Column(String(50),  nullable=True, default=None)
    hubungan_keluarga        = db.Column(String(50),  nullable=True, default=None)

    # Alamat
    alamat                   = db.Column(Text,        nullable=True, default=None)
    rt                       = db.Column(String(5),   nullable=True, default=None)
    rw                       = db.Column(String(5),   nullable=True, default=None)
    kelurahan                = db.Column(String(100), nullable=True, default=None)
    kecamatan                = db.Column(String(100), nullable=True, default=None)
    kabupaten_kota           = db.Column(String(100), nullable=True, default=None)
    provinsi                 = db.Column(String(100), nullable=True, default=None, index=True)
    kode_pos                 = db.Column(String(10),  nullable=True, default=None)

    # Data zakat/ekonomi
    penghasilan              = db.Column(Integer,     nullable=True, default=None)
    pekerjaan                = db.Column(String(100), nullable=True, default=None)
    pendidikan               = db.Column(String(100), nullable=True, default=None)

    # Raw payload dari ZAWA — simpan JSON asli agar tidak ada kolom yang hilang
    raw_data                 = db.Column(JSON,        nullable=True, default=None)

    # Metadata sync
    provinsi_slug            = db.Column(String(20),  nullable=True, default=None, index=True)
    synced_at                = db.Column(DateTime,    nullable=False, default=datetime.utcnow)
    created_at               = db.Column(DateTime,    nullable=False, default=datetime.utcnow)
    updated_at               = db.Column(DateTime,    nullable=True,  default=None, onupdate=datetime.utcnow)

    # Composite index untuk query provinsi + NIK (paling sering dipakai)
    __table_args__ = (
        Index('idx_anggota_provinsi_nik', 'provinsi_slug', 'nomor_induk_kependudukan'),
        Index('idx_anggota_provinsi_nkk', 'provinsi_slug', 'nomor_kartu_keluarga'),
        # FULLTEXT untuk search nama/alamat teks bebas (MySQL InnoDB)
        Index('ft_anggota_nama_alamat', 'nama', 'alamat', mysql_prefix='FULLTEXT'),
    )

    def to_dict(self) -> dict:
        """Kembalikan raw_data jika ada, fallback ke kolom-kolom model."""
        if self.raw_data and isinstance(self.raw_data, dict):
            return self.raw_data
        return {
            "nomor_induk_kependudukan": self.nomor_induk_kependudukan,
            "nomor_kartu_keluarga":     self.nomor_kartu_keluarga,
            "nama":                     self.nama,
            "jenis_kelamin":            self.jenis_kelamin,
            "tanggal_lahir":            str(self.tanggal_lahir) if self.tanggal_lahir else None,
            "tempat_lahir":             self.tempat_lahir,
            "agama":                    self.agama,
            "status_perkawinan":        self.status_perkawinan,
            "hubungan_keluarga":        self.hubungan_keluarga,
            "alamat":                   self.alamat,
            "rt":                       self.rt,
            "rw":                       self.rw,
            "kelurahan":                self.kelurahan,
            "kecamatan":                self.kecamatan,
            "kabupaten_kota":           self.kabupaten_kota,
            "provinsi":                 self.provinsi,
            "kode_pos":                 self.kode_pos,
            "penghasilan":              self.penghasilan,
            "pekerjaan":                self.pekerjaan,
            "pendidikan":               self.pendidikan,
        }

    def __repr__(self):
        return f'<ZawaAnggota {self.id} - {self.nama} ({self.nomor_induk_kependudukan})>'


class ZawaKeluarga(db.Model):
    """
    Tabel lokal cache data keluarga ZAWA dari API Kemenag.
    Di-sync via POST /api/v1/baseline/sync.
    Index di nomor_kartu_keluarga untuk pencarian cepat.
    """
    __tablename__ = 'zawa_keluarga'

    id                       = db.Column(BigInteger, primary_key=True, autoincrement=True)

    # Identitas utama
    nomor_kartu_keluarga     = db.Column(String(16),  nullable=True, default=None, index=True)
    kepala_keluarga          = db.Column(String(255), nullable=True, default=None)
    jumlah_anggota           = db.Column(Integer,     nullable=True, default=None)

    # Alamat
    alamat                   = db.Column(Text,        nullable=True, default=None)
    rt                       = db.Column(String(5),   nullable=True, default=None)
    rw                       = db.Column(String(5),   nullable=True, default=None)
    kelurahan                = db.Column(String(100), nullable=True, default=None)
    kecamatan                = db.Column(String(100), nullable=True, default=None)
    kabupaten_kota           = db.Column(String(100), nullable=True, default=None)
    provinsi                 = db.Column(String(100), nullable=True, default=None, index=True)
    kode_pos                 = db.Column(String(10),  nullable=True, default=None)

    # Raw payload dari ZAWA
    raw_data                 = db.Column(JSON,        nullable=True, default=None)

    # Metadata sync
    synced_at                = db.Column(DateTime,    nullable=False, default=datetime.utcnow)
    created_at               = db.Column(DateTime,    nullable=False, default=datetime.utcnow)
    updated_at               = db.Column(DateTime,    nullable=True,  default=None, onupdate=datetime.utcnow)

    # Index untuk pencarian
    __table_args__ = (
        Index('idx_keluarga_nkk_unik', 'nomor_kartu_keluarga', unique=True),
        # FULLTEXT untuk search nama kepala keluarga / alamat
        Index('ft_keluarga_nama_alamat', 'kepala_keluarga', 'alamat', mysql_prefix='FULLTEXT'),
    )

    def to_dict(self) -> dict:
        """Kembalikan raw_data jika ada, fallback ke kolom-kolom model."""
        if self.raw_data and isinstance(self.raw_data, dict):
            return self.raw_data
        return {
            "nomor_kartu_keluarga": self.nomor_kartu_keluarga,
            "kepala_keluarga":      self.kepala_keluarga,
            "jumlah_anggota":       self.jumlah_anggota,
            "alamat":               self.alamat,
            "rt":                   self.rt,
            "rw":                   self.rw,
            "kelurahan":            self.kelurahan,
            "kecamatan":            self.kecamatan,
            "kabupaten_kota":       self.kabupaten_kota,
            "provinsi":             self.provinsi,
            "kode_pos":             self.kode_pos,
        }

    def __repr__(self):
        return f'<ZawaKeluarga {self.id} - {self.kepala_keluarga} ({self.nomor_kartu_keluarga})>'


class ZawaSyncLog(db.Model):
    """
    Log setiap proses sync dari ZAWA API ke DB lokal.
    Digunakan untuk monitoring kapan terakhir sync dan berapa data yang masuk.
    """
    __tablename__ = 'zawa_sync_log'

    id            = db.Column(BigInteger,  primary_key=True, autoincrement=True)
    sync_type     = db.Column(String(20),  nullable=False)   # 'anggota' | 'keluarga' | 'all'
    provinsi_slug = db.Column(String(20),  nullable=True, default=None)  # None = semua provinsi
    status        = db.Column(String(10),  nullable=False, default='running')  # running|success|failed
    total_fetched = db.Column(Integer,     nullable=True, default=0)
    total_saved   = db.Column(Integer,     nullable=True, default=0)
    error_message = db.Column(Text,        nullable=True, default=None)
    started_at    = db.Column(DateTime,    nullable=False, default=datetime.utcnow)
    finished_at   = db.Column(DateTime,    nullable=True,  default=None)

    def duration_seconds(self) -> float | None:
        if self.finished_at and self.started_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None

    def __repr__(self):
        return f'<ZawaSyncLog {self.id} {self.sync_type} {self.status}>'
