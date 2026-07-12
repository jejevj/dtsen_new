from ..extensions import db
from datetime import datetime
from sqlalchemy import Index, BigInteger, String, Text, Date, DateTime, Integer, JSON, Numeric


class ZawaAnggota(db.Model):
    """
    Cache data anggota ZAWA. Field disesuaikan dengan response nyata
    dari endpoint GET zawa/anggota & zawa/anggota-by-nik.
    Diisi via search-on-demand: setiap kali ZAWA berhasil diquery,
    hasilnya disimpan di sini agar request berikutnya tidak hit ZAWA lagi.
    """
    __tablename__ = 'zawa_anggota'

    id = db.Column(BigInteger, primary_key=True, autoincrement=True)

    # ── Identitas utama
    nomor_induk_kependudukan  = db.Column(String(20),  nullable=True, default=None)
    nomor_kartu_keluarga      = db.Column(String(20),  nullable=True, default=None)
    nama                      = db.Column(String(255), nullable=True, default=None)
    jenis_kelamin             = db.Column(String(5),   nullable=True, default=None)
    tanggal_lahir             = db.Column(Date,        nullable=True, default=None)
    status_kawin              = db.Column(String(5),   nullable=True, default=None)
    status_hubungan_keluarga  = db.Column(String(5),   nullable=True, default=None)

    # ── Alamat KTP
    alamat_ktp                = db.Column(Text,        nullable=True, default=None)
    dusun_ktp                 = db.Column(String(100), nullable=True, default=None)
    rt_ktp                    = db.Column(Integer,     nullable=True, default=None)
    rw_ktp                    = db.Column(Integer,     nullable=True, default=None)
    kelurahan_desa_ktp        = db.Column(String(100), nullable=True, default=None)
    kecamatan_ktp             = db.Column(String(100), nullable=True, default=None)
    kabupaten_kota_ktp        = db.Column(String(100), nullable=True, default=None)
    provinsi_ktp              = db.Column(String(100), nullable=True, default=None)
    kode_provinsi_ktp         = db.Column(String(10),  nullable=True, default=None)
    kode_kabupaten_kota_ktp   = db.Column(String(10),  nullable=True, default=None)
    kode_kecamatan_ktp        = db.Column(String(10),  nullable=True, default=None)
    kode_kelurahan_desa_ktp   = db.Column(String(15),  nullable=True, default=None)

    # ── Pendidikan
    partisipasi_sekolah                = db.Column(String(5),  nullable=True, default=None)
    jenjang_tertinggi_yang_diduduki    = db.Column(Integer,    nullable=True, default=None)
    kelas_tertinggi_yang_diduduki      = db.Column(Integer,    nullable=True, default=None)
    ijazah_tertinggi_yang_dimiliki     = db.Column(Integer,    nullable=True, default=None)

    # ── Pekerjaan & usaha
    status_bekerja                                  = db.Column(String(5),  nullable=True, default=None)
    status_dalam_pekerjaan_utama                    = db.Column(String(5),  nullable=True, default=None)
    lapangan_usaha_dari_pekerjaan_utama             = db.Column(Integer,    nullable=True, default=None)
    lapangan_usaha_dari_usaha_utama                 = db.Column(Integer,    nullable=True, default=None)
    kepemilikan_usaha                               = db.Column(String(5),  nullable=True, default=None)
    jumlah_usaha                                    = db.Column(Integer,    nullable=True, default=None)
    jumlah_pekerja_yang_dibayar_dari_usaha_utama    = db.Column(Integer,    nullable=True, default=None)
    jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama = db.Column(Integer, nullable=True, default=None)
    omzet_usaha_utama                               = db.Column(Numeric(15, 2), nullable=True, default=None)
    id_pelanggan_pln                                = db.Column(String(20), nullable=True, default=None)

    # ── Kesehatan & disabilitas
    kondisi_gizi              = db.Column(String(5),  nullable=True, default=None)
    penyakit_kronis           = db.Column(Integer,    nullable=True, default=None)
    penglihatan               = db.Column(String(5),  nullable=True, default=None)
    pendengaran               = db.Column(String(5),  nullable=True, default=None)
    berjalan_atau_naik_tangga = db.Column(String(5),  nullable=True, default=None)
    menggunakan_tangan_jari   = db.Column(String(5),  nullable=True, default=None)
    mengingat_berkonsentrasi  = db.Column(String(5),  nullable=True, default=None)
    berbicara_komunikasi      = db.Column(String(5),  nullable=True, default=None)
    belajar_kemampuan_intelektual = db.Column(String(5), nullable=True, default=None)
    mengurus_diri             = db.Column(String(5),  nullable=True, default=None)
    kesedihan_depresi         = db.Column(String(5),  nullable=True, default=None)
    pengendalian_perilaku     = db.Column(String(5),  nullable=True, default=None)

    # ── Bansos
    pbi_nas   = db.Column(String(5), nullable=True, default=None)
    pbi_pemda = db.Column(String(5), nullable=True, default=None)

    # ── Raw JSON asli dari ZAWA (agar tidak ada field yang hilang)
    raw_data = db.Column(JSON, nullable=True, default=None)

    # ── Metadata sync
    provinsi_slug = db.Column(String(20),  nullable=True, default=None)
    synced_at     = db.Column(DateTime,    nullable=False, default=datetime.utcnow)
    created_at    = db.Column(DateTime,    nullable=False, default=datetime.utcnow)
    updated_at    = db.Column(DateTime,    nullable=True,  default=None, onupdate=datetime.utcnow)

    __table_args__ = (
        # Index tunggal untuk lookup cepat
        Index('idx_anggota_nik',          'nomor_induk_kependudukan'),
        Index('idx_anggota_nkk',          'nomor_kartu_keluarga'),
        Index('idx_anggota_provinsi_slug','provinsi_slug'),
        # Composite: filter provinsi + cari NIK
        Index('idx_anggota_slug_nik',     'provinsi_slug', 'nomor_induk_kependudukan'),
        Index('idx_anggota_slug_nkk',     'provinsi_slug', 'nomor_kartu_keluarga'),
        # FULLTEXT untuk search nama bebas
        Index('ft_anggota_nama',          'nama', mysql_prefix='FULLTEXT'),
    )

    def to_dict(self) -> dict:
        """Kembalikan raw_data jika ada, fallback ke mapping kolom model."""
        if self.raw_data and isinstance(self.raw_data, dict):
            return self.raw_data
        return {
            "nomor_induk_kependudukan":  self.nomor_induk_kependudukan,
            "nomor_kartu_keluarga":      self.nomor_kartu_keluarga,
            "nama":                      self.nama,
            "jenis_kelamin":             self.jenis_kelamin,
            "tanggal_lahir":             str(self.tanggal_lahir) if self.tanggal_lahir else None,
            "status_kawin":              self.status_kawin,
            "status_hubungan_keluarga":  self.status_hubungan_keluarga,
            "alamat_ktp":                self.alamat_ktp,
            "kelurahan_desa_ktp":        self.kelurahan_desa_ktp,
            "kecamatan_ktp":             self.kecamatan_ktp,
            "kabupaten_kota_ktp":        self.kabupaten_kota_ktp,
            "provinsi_ktp":              self.provinsi_ktp,
            "pbi_nas":                   self.pbi_nas,
            "pbi_pemda":                 self.pbi_pemda,
        }

    def __repr__(self):
        return f'<ZawaAnggota {self.id} - {self.nama} NIK={self.nomor_induk_kependudukan}>'


class ZawaKeluarga(db.Model):
    """
    Cache data keluarga ZAWA. Field disesuaikan dengan response nyata
    dari endpoint GET zawa/keluarga & zawa/keluarga-by-nik.
    Diisi via search-on-demand: setiap kali ZAWA berhasil diquery,
    hasilnya disimpan di sini agar request berikutnya tidak hit ZAWA lagi.
    """
    __tablename__ = 'zawa_keluarga'

    id = db.Column(BigInteger, primary_key=True, autoincrement=True)

    # ── Identitas utama
    nomor_kartu_keluarga   = db.Column(String(20),  nullable=True, default=None)
    nama_anggota_keluarga  = db.Column(String(255), nullable=True, default=None)  # kepala keluarga
    jumlah_anggota_keluarga = db.Column(Integer,   nullable=True, default=None)

    # ── Alamat
    alamat           = db.Column(Text,        nullable=True, default=None)
    kelurahan_desa   = db.Column(String(100), nullable=True, default=None)
    kecamatan        = db.Column(String(100), nullable=True, default=None)
    kabupaten_kota   = db.Column(String(100), nullable=True, default=None)
    provinsi         = db.Column(String(100), nullable=True, default=None)
    kode_provinsi    = db.Column(String(10),  nullable=True, default=None)
    kode_kabupaten_kota  = db.Column(String(10),  nullable=True, default=None)
    kode_kecamatan   = db.Column(String(10),  nullable=True, default=None)
    kode_kelurahan_desa  = db.Column(String(15),  nullable=True, default=None)

    # ── Kondisi rumah
    luas_lantai                = db.Column(Integer,    nullable=True, default=None)
    jenis_lantai_terluas       = db.Column(Integer,    nullable=True, default=None)
    jenis_dinding_terluas      = db.Column(Integer,    nullable=True, default=None)
    jenis_atap_terluas         = db.Column(Integer,    nullable=True, default=None)
    status_kepemilikan_rumah   = db.Column(String(5),  nullable=True, default=None)
    fasilitas_bab              = db.Column(String(5),  nullable=True, default=None)
    jenis_kloset               = db.Column(String(5),  nullable=True, default=None)
    pembuangan_akhir_tinja     = db.Column(String(5),  nullable=True, default=None)
    sumber_air_minum_utama     = db.Column(Integer,    nullable=True, default=None)
    sumber_penerangan_utama    = db.Column(String(5),  nullable=True, default=None)
    bahan_bakar_utama_memasak  = db.Column(Integer,    nullable=True, default=None)
    daya_terpasang             = db.Column(Integer,    nullable=True, default=None)
    id_pelanggan_pln           = db.Column(String(20), nullable=True, default=None)

    # ── Aset bergerak
    aset_bergerak_sepeda_motor      = db.Column(String(5), nullable=True, default=None)
    aset_bergerak_mobil             = db.Column(String(5), nullable=True, default=None)
    aset_bergerak_sepeda            = db.Column(String(5), nullable=True, default=None)
    aset_bergerak_perahu            = db.Column(String(5), nullable=True, default=None)
    aset_bergerak_kapal_perahu_motor = db.Column(String(5), nullable=True, default=None)
    aset_bergerak_smartphone        = db.Column(String(5), nullable=True, default=None)
    aset_bergerak_komputer_laptop_tablet = db.Column(String(5), nullable=True, default=None)
    aset_bergerak_tv_datar          = db.Column(String(5), nullable=True, default=None)
    aset_bergerak_lemari_es         = db.Column(String(5), nullable=True, default=None)
    aset_bergerak_ac                = db.Column(String(5), nullable=True, default=None)
    aset_bergerak_pemanas_air       = db.Column(String(5), nullable=True, default=None)
    aset_bergerak_tabung_gas        = db.Column(String(5), nullable=True, default=None)
    aset_bergerak_telepon_rumah     = db.Column(String(5), nullable=True, default=None)
    aset_bergerak_emas_perhiasan    = db.Column(String(5), nullable=True, default=None)

    # ── Aset tidak bergerak
    aset_tidak_bergerak_rumah_lainnya  = db.Column(String(5), nullable=True, default=None)
    aset_tidak_bergerak_lahan_lainnya  = db.Column(String(5), nullable=True, default=None)
    kepemilikan_aset                   = db.Column(String(5), nullable=True, default=None)

    # ── Ternak
    jumlah_ternak_sapi          = db.Column(Integer, nullable=True, default=None)
    jumlah_ternak_kerbau        = db.Column(Integer, nullable=True, default=None)
    jumlah_ternak_kuda          = db.Column(Integer, nullable=True, default=None)
    jumlah_ternak_kambing_domba = db.Column(Integer, nullable=True, default=None)
    jumlah_ternak_babi          = db.Column(Integer, nullable=True, default=None)

    # ── Bansos & kesejahteraan
    pbi_nas        = db.Column(String(5), nullable=True, default=None)
    pbi_pemda      = db.Column(String(5), nullable=True, default=None)
    desil_nasional = db.Column(String(5), nullable=True, default=None)

    # ── Raw JSON asli dari ZAWA
    raw_data = db.Column(JSON, nullable=True, default=None)

    # ── Metadata sync
    synced_at  = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(DateTime, nullable=True,  default=None, onupdate=datetime.utcnow)

    __table_args__ = (
        # NKK unik — tidak boleh double simpan
        Index('idx_keluarga_nkk_unik',    'nomor_kartu_keluarga', unique=True),
        Index('idx_keluarga_provinsi',     'provinsi'),
        Index('idx_keluarga_kode_provinsi','kode_provinsi'),
        # FULLTEXT untuk search nama kepala keluarga / alamat
        Index('ft_keluarga_nama_alamat',   'nama_anggota_keluarga', 'alamat', mysql_prefix='FULLTEXT'),
    )

    def to_dict(self) -> dict:
        """Kembalikan raw_data jika ada, fallback ke mapping kolom model."""
        if self.raw_data and isinstance(self.raw_data, dict):
            return self.raw_data
        return {
            "nomor_kartu_keluarga":    self.nomor_kartu_keluarga,
            "nama_anggota_keluarga":   self.nama_anggota_keluarga,
            "jumlah_anggota_keluarga": self.jumlah_anggota_keluarga,
            "alamat":                  self.alamat,
            "kelurahan_desa":          self.kelurahan_desa,
            "kecamatan":               self.kecamatan,
            "kabupaten_kota":          self.kabupaten_kota,
            "provinsi":                self.provinsi,
            "desil_nasional":          self.desil_nasional,
            "pbi_nas":                 self.pbi_nas,
            "pbi_pemda":               self.pbi_pemda,
        }

    def __repr__(self):
        return f'<ZawaKeluarga {self.id} - {self.nama_anggota_keluarga} NKK={self.nomor_kartu_keluarga}>'


class ZawaSyncLog(db.Model):
    """
    Log setiap proses cache/sync dari ZAWA API ke DB lokal.
    """
    __tablename__ = 'zawa_sync_log'

    id            = db.Column(BigInteger, primary_key=True, autoincrement=True)
    sync_type     = db.Column(String(20), nullable=False)          # 'anggota' | 'keluarga'
    provinsi_slug = db.Column(String(20), nullable=True, default=None)
    status        = db.Column(String(10), nullable=False, default='running')  # running|success|failed
    total_fetched = db.Column(Integer,    nullable=True, default=0)
    total_saved   = db.Column(Integer,    nullable=True, default=0)
    error_message = db.Column(Text,       nullable=True, default=None)
    started_at    = db.Column(DateTime,   nullable=False, default=datetime.utcnow)
    finished_at   = db.Column(DateTime,   nullable=True,  default=None)

    __table_args__ = (
        Index('idx_synclog_type_status', 'sync_type', 'status'),
        Index('idx_synclog_started',     'started_at'),
    )

    def duration_seconds(self) -> float | None:
        if self.finished_at and self.started_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None

    def __repr__(self):
        return f'<ZawaSyncLog {self.id} {self.sync_type} {self.status}>'
