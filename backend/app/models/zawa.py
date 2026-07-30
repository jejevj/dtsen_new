from app.extensions import db
from datetime import datetime
from decimal import Decimal, InvalidOperation


def _parse_date(val) -> str | None:
    """Konversi ISO datetime string ke date string YYYY-MM-DD."""
    if not val:
        return None
    s = str(val).strip()
    return s[:10] if len(s) >= 10 else s or None


def _i(val) -> int | None:
    if val is None or str(val).strip() == '':
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _d(val) -> Decimal | None:
    if val is None or str(val).strip() == '':
        return None
    try:
        return Decimal(str(val))
    except (InvalidOperation, TypeError):
        return None


def _s(val) -> str | None:
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def _kode(val) -> str | None:
    """Normalisasi kode wilayah: hapus titik agar konsisten dengan format plain.
    Contoh: '15.08.03' -> '150803', '1508' -> '1508'
    Ini memastikan composite index idx_anggota_wilayah_ktp dapat dipakai
    secara optimal oleh MySQL (exact match, bukan OR).
    """
    if val is None:
        return None
    s = str(val).strip().replace('.', '')
    return s if s else None


class ZawaAnggota(db.Model):
    __tablename__ = "zawa_anggota"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    nomor_induk_kependudukan = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nomor_kartu_keluarga     = db.Column(db.String(20), nullable=True, index=True)
    nama                     = db.Column(db.String(255), nullable=True)
    jenis_kelamin            = db.Column(db.String(2),   nullable=True)
    tanggal_lahir            = db.Column(db.String(30),  nullable=True)
    status_kawin             = db.Column(db.String(5),   nullable=True)
    status_hubungan_keluarga = db.Column(db.String(5),   nullable=True)

    alamat_ktp               = db.Column(db.Text,        nullable=True)
    dusun_ktp                = db.Column(db.String(100), nullable=True)
    rt_ktp                   = db.Column(db.Integer,     nullable=True)
    rw_ktp                   = db.Column(db.Integer,     nullable=True)
    kelurahan_desa_ktp       = db.Column(db.String(100), nullable=True)
    kecamatan_ktp            = db.Column(db.String(100), nullable=True)
    kabupaten_kota_ktp       = db.Column(db.String(100), nullable=True)
    provinsi_ktp             = db.Column(db.String(100), nullable=True)
    kode_kelurahan_desa_ktp  = db.Column(db.String(15),  nullable=True)
    kode_kecamatan_ktp       = db.Column(db.String(10),  nullable=True)
    kode_kabupaten_kota_ktp  = db.Column(db.String(10),  nullable=True)
    kode_provinsi_ktp        = db.Column(db.String(10),  nullable=True)

    partisipasi_sekolah             = db.Column(db.String(5), nullable=True)
    jenjang_tertinggi_yang_diduduki = db.Column(db.Integer,   nullable=True)
    kelas_tertinggi_yang_diduduki   = db.Column(db.Integer,   nullable=True)
    ijazah_tertinggi_yang_dimiliki  = db.Column(db.Integer,   nullable=True)

    status_bekerja                                     = db.Column(db.String(5),      nullable=True)
    status_dalam_pekerjaan_utama                       = db.Column(db.String(5),      nullable=True)
    lapangan_usaha_dari_pekerjaan_utama                = db.Column(db.Integer,        nullable=True)
    lapangan_usaha_dari_usaha_utama                    = db.Column(db.Integer,        nullable=True)
    kepemilikan_usaha                                  = db.Column(db.String(5),      nullable=True)
    jumlah_usaha                                       = db.Column(db.Integer,        nullable=True)
    omzet_usaha_utama                                  = db.Column(db.Numeric(15, 2), nullable=True)
    jumlah_pekerja_yang_dibayar_dari_usaha_utama       = db.Column(db.Integer,        nullable=True)
    jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama = db.Column(db.Integer,        nullable=True)

    penglihatan               = db.Column(db.String(5), nullable=True)
    pendengaran               = db.Column(db.String(5), nullable=True)
    berjalan_atau_naik_tangga = db.Column(db.String(5), nullable=True)
    menggunakan_tangan_jari   = db.Column(db.String(5), nullable=True)
    mengingat_berkonsentrasi  = db.Column(db.String(5), nullable=True)
    mengurus_diri             = db.Column(db.String(5), nullable=True)
    berbicara_komunikasi      = db.Column(db.String(5), nullable=True)
    belajar_kemampuan_intelektual = db.Column(db.String(5), nullable=True)
    pengendalian_perilaku     = db.Column(db.String(5), nullable=True)
    kesedihan_depresi         = db.Column(db.String(5), nullable=True)

    kondisi_gizi    = db.Column(db.String(5), nullable=True)
    penyakit_kronis = db.Column(db.Integer,   nullable=True)

    pbi_nas          = db.Column(db.String(5),  nullable=True)
    pbi_pemda        = db.Column(db.String(5),  nullable=True)
    id_pelanggan_pln = db.Column(db.String(20), nullable=True)

    provinsi_slug = db.Column(db.String(20), nullable=True, index=True)
    synced_at     = db.Column(db.DateTime,   default=datetime.utcnow)

    __table_args__ = (
        db.Index("idx_anggota_prov_nik", "provinsi_slug", "nomor_induk_kependudukan"),
    )

    @classmethod
    def from_api(cls, item: dict, provinsi_slug: str = None):
        raw_tgl = item.get("tanggal_lahir") or ""
        tgl = str(raw_tgl).strip()[:10] if raw_tgl else None
        return cls(
            nomor_induk_kependudukan                           = str(item.get("nomor_induk_kependudukan") or ""),
            nomor_kartu_keluarga                               = _s(item.get("nomor_kartu_keluarga")),
            nama                                               = _s(item.get("nama")),
            jenis_kelamin                                      = _s(item.get("jenis_kelamin")),
            tanggal_lahir                                      = tgl,
            status_kawin                                       = _s(item.get("status_kawin")),
            status_hubungan_keluarga                           = _s(item.get("status_hubungan_keluarga")),
            alamat_ktp                                         = _s(item.get("alamat_ktp")),
            dusun_ktp                                          = _s(item.get("dusun_ktp")),
            rt_ktp                                             = _i(item.get("rt_ktp")),
            rw_ktp                                             = _i(item.get("rw_ktp")),
            kelurahan_desa_ktp                                 = _s(item.get("kelurahan_desa_ktp")),
            kecamatan_ktp                                      = _s(item.get("kecamatan_ktp")),
            kabupaten_kota_ktp                                 = _s(item.get("kabupaten_kota_ktp")),
            provinsi_ktp                                       = _s(item.get("provinsi_ktp")),
            # Kode wilayah selalu disimpan tanpa titik (plain) agar
            # idx_anggota_wilayah_ktp dapat dipakai dengan exact match.
            kode_kelurahan_desa_ktp                            = _kode(item.get("kode_kelurahan_desa_ktp")),
            kode_kecamatan_ktp                                 = _kode(item.get("kode_kecamatan_ktp")),
            kode_kabupaten_kota_ktp                            = _kode(item.get("kode_kabupaten_kota_ktp")),
            kode_provinsi_ktp                                  = _kode(item.get("kode_provinsi_ktp")),
            partisipasi_sekolah                                = _s(item.get("partisipasi_sekolah")),
            jenjang_tertinggi_yang_diduduki                    = _i(item.get("jenjang_tertinggi_yang_diduduki")),
            kelas_tertinggi_yang_diduduki                      = _i(item.get("kelas_tertinggi_yang_diduduki")),
            ijazah_tertinggi_yang_dimiliki                     = _i(item.get("ijazah_tertinggi_yang_dimiliki")),
            status_bekerja                                     = _s(item.get("status_bekerja")),
            status_dalam_pekerjaan_utama                       = _s(item.get("status_dalam_pekerjaan_utama")),
            lapangan_usaha_dari_pekerjaan_utama                = _i(item.get("lapangan_usaha_dari_pekerjaan_utama")),
            lapangan_usaha_dari_usaha_utama                    = _i(item.get("lapangan_usaha_dari_usaha_utama")),
            kepemilikan_usaha                                  = _s(item.get("kepemilikan_usaha")),
            jumlah_usaha                                       = _i(item.get("jumlah_usaha")),
            omzet_usaha_utama                                  = _d(item.get("omzet_usaha_utama")),
            jumlah_pekerja_yang_dibayar_dari_usaha_utama       = _i(item.get("jumlah_pekerja_yang_dibayar_dari_usaha_utama")),
            jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama = _i(item.get("jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama")),
            penglihatan                                        = _s(item.get("penglihatan")),
            pendengaran                                        = _s(item.get("pendengaran")),
            berjalan_atau_naik_tangga                          = _s(item.get("berjalan_atau_naik_tangga")),
            menggunakan_tangan_jari                            = _s(item.get("menggunakan_tangan_jari")),
            mengingat_berkonsentrasi                           = _s(item.get("mengingat_berkonsentrasi")),
            mengurus_diri                                      = _s(item.get("mengurus_diri")),
            berbicara_komunikasi                               = _s(item.get("berbicara_komunikasi")),
            belajar_kemampuan_intelektual                      = _s(item.get("belajar_kemampuan_intelektual")),
            pengendalian_perilaku                              = _s(item.get("pengendalian_perilaku")),
            kesedihan_depresi                                  = _s(item.get("kesedihan_depresi")),
            kondisi_gizi                                       = _s(item.get("kondisi_gizi")),
            penyakit_kronis                                    = _i(item.get("penyakit_kronis")),
            pbi_nas                                            = _s(item.get("pbi_nas")),
            pbi_pemda                                          = _s(item.get("pbi_pemda")),
            id_pelanggan_pln                                   = _s(item.get("id_pelanggan_pln")),
            provinsi_slug                                      = provinsi_slug,
        )


class ZawaKeluarga(db.Model):
    __tablename__ = "zawa_keluarga"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    nomor_kartu_keluarga    = db.Column(db.String(20),  unique=True, nullable=False, index=True)
    nama_anggota_keluarga   = db.Column(db.String(255), nullable=True)
    jumlah_anggota_keluarga = db.Column(db.Integer,     nullable=True)
    alamat                  = db.Column(db.Text,        nullable=True)
    kelurahan_desa          = db.Column(db.String(100), nullable=True)
    kecamatan               = db.Column(db.String(100), nullable=True)
    kabupaten_kota          = db.Column(db.String(100), nullable=True)
    provinsi                = db.Column(db.String(100), nullable=True, index=True)
    kode_kelurahan_desa     = db.Column(db.String(15),  nullable=True)
    kode_kecamatan          = db.Column(db.String(10),  nullable=True)
    kode_kabupaten_kota     = db.Column(db.String(10),  nullable=True)
    kode_provinsi           = db.Column(db.String(10),  nullable=True)

    luas_lantai              = db.Column(db.Integer,    nullable=True)
    jenis_lantai_terluas     = db.Column(db.Integer,    nullable=True)
    jenis_dinding_terluas    = db.Column(db.Integer,    nullable=True)
    jenis_atap_terluas       = db.Column(db.Integer,    nullable=True)
    jenis_kloset             = db.Column(db.String(5),  nullable=True)
    fasilitas_bab            = db.Column(db.String(5),  nullable=True)
    sumber_air_minum_utama   = db.Column(db.Integer,    nullable=True)
    sumber_penerangan_utama  = db.Column(db.String(5),  nullable=True)
    bahan_bakar_utama_memasak = db.Column(db.Integer,   nullable=True)
    daya_terpasang           = db.Column(db.Integer,    nullable=True)
    pembuangan_akhir_tinja   = db.Column(db.String(5),  nullable=True)
    status_kepemilikan_rumah = db.Column(db.String(5),  nullable=True)
    kepemilikan_aset         = db.Column(db.String(5),  nullable=True)

    aset_bergerak_sepeda_motor           = db.Column(db.String(5), nullable=True)
    aset_bergerak_mobil                  = db.Column(db.String(5), nullable=True)
    aset_bergerak_sepeda                 = db.Column(db.String(5), nullable=True)
    aset_bergerak_perahu                 = db.Column(db.String(5), nullable=True)
    aset_bergerak_kapal_perahu_motor     = db.Column(db.String(5), nullable=True)
    aset_bergerak_smartphone             = db.Column(db.String(5), nullable=True)
    aset_bergerak_komputer_laptop_tablet = db.Column(db.String(5), nullable=True)
    aset_bergerak_lemari_es              = db.Column(db.String(5), nullable=True)
    aset_bergerak_ac                     = db.Column(db.String(5), nullable=True)
    aset_bergerak_tv_datar               = db.Column(db.String(5), nullable=True)
    aset_bergerak_emas_perhiasan         = db.Column(db.String(5), nullable=True)
    aset_bergerak_tabung_gas             = db.Column(db.String(5), nullable=True)
    aset_bergerak_pemanas_air            = db.Column(db.String(5), nullable=True)
    aset_bergerak_telepon_rumah          = db.Column(db.String(5), nullable=True)

    aset_tidak_bergerak_rumah_lainnya  = db.Column(db.String(5), nullable=True)
    aset_tidak_bergerak_lahan_lainnya  = db.Column(db.String(5), nullable=True)

    jumlah_ternak_sapi          = db.Column(db.Integer, nullable=True)
    jumlah_ternak_kerbau        = db.Column(db.Integer, nullable=True)
    jumlah_ternak_kuda          = db.Column(db.Integer, nullable=True)
    jumlah_ternak_kambing_domba = db.Column(db.Integer, nullable=True)
    jumlah_ternak_babi          = db.Column(db.Integer, nullable=True)

    pbi_nas        = db.Column(db.String(5),  nullable=True)
    pbi_pemda      = db.Column(db.String(5),  nullable=True)
    desil_nasional = db.Column(db.String(5),  nullable=True)
    id_pelanggan_pln = db.Column(db.String(20), nullable=True)

    synced_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def from_api(cls, item: dict):
        return cls(
            nomor_kartu_keluarga         = str(item.get("nomor_kartu_keluarga") or "").strip(),
            nama_anggota_keluarga        = _s(item.get("nama_anggota_keluarga")),
            jumlah_anggota_keluarga      = _i(item.get("jumlah_anggota_keluarga")),
            alamat                       = _s(item.get("alamat")),
            kelurahan_desa               = _s(item.get("kelurahan_desa")),
            kecamatan                    = _s(item.get("kecamatan")),
            kabupaten_kota               = _s(item.get("kabupaten_kota")),
            provinsi                     = _s(item.get("provinsi")),
            kode_kelurahan_desa          = _s(item.get("kode_kelurahan_desa")),
            kode_kecamatan               = _s(item.get("kode_kecamatan")),
            kode_kabupaten_kota          = _s(item.get("kode_kabupaten_kota")),
            kode_provinsi                = _s(item.get("kode_provinsi")),
            luas_lantai                  = _i(item.get("luas_lantai")),
            jenis_lantai_terluas         = _i(item.get("jenis_lantai_terluas")),
            jenis_dinding_terluas        = _i(item.get("jenis_dinding_terluas")),
            jenis_atap_terluas           = _i(item.get("jenis_atap_terluas")),
            jenis_kloset                 = _s(item.get("jenis_kloset")),
            fasilitas_bab                = _s(item.get("fasilitas_bab")),
            sumber_air_minum_utama       = _i(item.get("sumber_air_minum_utama")),
            sumber_penerangan_utama      = _s(item.get("sumber_penerangan_utama")),
            bahan_bakar_utama_memasak    = _i(item.get("bahan_bakar_utama_memasak")),
            daya_terpasang               = _i(item.get("daya_terpasang")),
            pembuangan_akhir_tinja       = _s(item.get("pembuangan_akhir_tinja")),
            status_kepemilikan_rumah     = _s(item.get("status_kepemilikan_rumah")),
            kepemilikan_aset             = _s(item.get("kepemilikan_aset")),
            aset_bergerak_sepeda_motor           = _s(item.get("aset_bergerak_sepeda_motor")),
            aset_bergerak_mobil                  = _s(item.get("aset_bergerak_mobil")),
            aset_bergerak_sepeda                 = _s(item.get("aset_bergerak_sepeda")),
            aset_bergerak_perahu                 = _s(item.get("aset_bergerak_perahu")),
            aset_bergerak_kapal_perahu_motor     = _s(item.get("aset_bergerak_kapal_perahu_motor")),
            aset_bergerak_smartphone             = _s(item.get("aset_bergerak_smartphone")),
            aset_bergerak_komputer_laptop_tablet = _s(item.get("aset_bergerak_komputer_laptop_tablet")),
            aset_bergerak_lemari_es              = _s(item.get("aset_bergerak_lemari_es")),
            aset_bergerak_ac                     = _s(item.get("aset_bergerak_ac")),
            aset_bergerak_tv_datar               = _s(item.get("aset_bergerak_tv_datar")),
            aset_bergerak_emas_perhiasan         = _s(item.get("aset_bergerak_emas_perhiasan")),
            aset_bergerak_tabung_gas             = _s(item.get("aset_bergerak_tabung_gas")),
            aset_bergerak_pemanas_air            = _s(item.get("aset_bergerak_pemanas_air")),
            aset_bergerak_telepon_rumah          = _s(item.get("aset_bergerak_telepon_rumah")),
            aset_tidak_bergerak_rumah_lainnya    = _s(item.get("aset_tidak_bergerak_rumah_lainnya")),
            aset_tidak_bergerak_lahan_lainnya    = _s(item.get("aset_tidak_bergerak_lahan_lainnya")),
            jumlah_ternak_sapi          = _i(item.get("jumlah_ternak_sapi")),
            jumlah_ternak_kerbau        = _i(item.get("jumlah_ternak_kerbau")),
            jumlah_ternak_kuda          = _i(item.get("jumlah_ternak_kuda")),
            jumlah_ternak_kambing_domba = _i(item.get("jumlah_ternak_kambing_domba")),
            jumlah_ternak_babi          = _i(item.get("jumlah_ternak_babi")),
            pbi_nas                     = _s(item.get("pbi_nas")),
            pbi_pemda                   = _s(item.get("pbi_pemda")),
            desil_nasional              = _s(item.get("desil_nasional")),
            id_pelanggan_pln            = _s(item.get("id_pelanggan_pln")),
        )


class ZawaSyncLog(db.Model):
    """Log untuk mencatat setiap proses sinkronisasi data ZAWA."""
    __tablename__ = "zawa_sync_log"

    id         = db.Column(db.Integer,     primary_key=True, autoincrement=True)
    sync_type  = db.Column(db.String(50),  nullable=False)          # 'anggota' | 'keluarga'
    status     = db.Column(db.String(20),  nullable=False)          # 'running' | 'success' | 'failed'
    provinsi   = db.Column(db.String(100), nullable=True)
    total_rows = db.Column(db.Integer,     nullable=True)
    message    = db.Column(db.Text,        nullable=True)
    started_at = db.Column(db.DateTime,    default=datetime.utcnow)
    finished_at = db.Column(db.DateTime,   nullable=True)

    def __repr__(self):
        return f"<ZawaSyncLog {self.sync_type} {self.status} @ {self.started_at}>"
