from app.extensions import db
from datetime import datetime


def _parse_date(val) -> str | None:
    """Konversi ISO datetime string ke date string YYYY-MM-DD.
    Contoh: '2023-10-09T00:00:00Z' -> '2023-10-09'
    """
    if not val:
        return None
    s = str(val).strip()
    if not s:
        return None
    # Ambil 10 karakter pertama saja (YYYY-MM-DD)
    return s[:10] if len(s) >= 10 else s


class ZawaAnggota(db.Model):
    __tablename__ = "zawa_anggota"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # Identitas utama
    nomor_induk_kependudukan = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nomor_kartu_keluarga     = db.Column(db.String(20), nullable=True,  index=True)
    nama                     = db.Column(db.String(255), nullable=True)
    jenis_kelamin            = db.Column(db.String(2),   nullable=True)
    tanggal_lahir            = db.Column(db.String(30),  nullable=True)
    status_kawin             = db.Column(db.String(5),   nullable=True)
    status_hubungan_keluarga = db.Column(db.String(5),   nullable=True)

    # Alamat KTP
    alamat_ktp               = db.Column(db.String(500), nullable=True)
    dusun_ktp                = db.Column(db.String(100), nullable=True)
    rt_ktp                   = db.Column(db.String(5),   nullable=True)
    rw_ktp                   = db.Column(db.String(5),   nullable=True)
    kelurahan_desa_ktp       = db.Column(db.String(100), nullable=True)
    kecamatan_ktp            = db.Column(db.String(100), nullable=True)
    kabupaten_kota_ktp       = db.Column(db.String(100), nullable=True)
    provinsi_ktp             = db.Column(db.String(100), nullable=True)
    kode_kelurahan_desa_ktp  = db.Column(db.String(20),  nullable=True)
    kode_kecamatan_ktp       = db.Column(db.String(20),  nullable=True)
    kode_kabupaten_kota_ktp  = db.Column(db.String(20),  nullable=True)
    kode_provinsi_ktp        = db.Column(db.String(5),   nullable=True)

    # Pendidikan
    partisipasi_sekolah             = db.Column(db.String(5),  nullable=True)
    jenjang_tertinggi_yang_diduduki = db.Column(db.String(5),  nullable=True)
    kelas_tertinggi_yang_diduduki   = db.Column(db.String(5),  nullable=True)
    ijazah_tertinggi_yang_dimiliki  = db.Column(db.String(5),  nullable=True)

    # Pekerjaan
    status_bekerja                                = db.Column(db.String(5),  nullable=True)
    status_dalam_pekerjaan_utama                  = db.Column(db.String(5),  nullable=True)
    lapangan_usaha_dari_pekerjaan_utama           = db.Column(db.String(5),  nullable=True)
    lapangan_usaha_dari_usaha_utama               = db.Column(db.String(5),  nullable=True)
    kepemilikan_usaha                             = db.Column(db.String(5),  nullable=True)
    jumlah_usaha                                  = db.Column(db.String(10), nullable=True)
    omzet_usaha_utama                             = db.Column(db.String(20), nullable=True)
    jumlah_pekerja_yang_dibayar_dari_usaha_utama  = db.Column(db.String(10), nullable=True)
    jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama = db.Column(db.String(10), nullable=True)

    # Disabilitas
    penglihatan              = db.Column(db.String(5), nullable=True)
    pendengaran              = db.Column(db.String(5), nullable=True)
    berjalan_atau_naik_tangga = db.Column(db.String(5), nullable=True)
    menggunakan_tangan_jari  = db.Column(db.String(5), nullable=True)
    mengingat_berkonsentrasi = db.Column(db.String(5), nullable=True)
    mengurus_diri            = db.Column(db.String(5), nullable=True)
    berbicara_komunikasi     = db.Column(db.String(5), nullable=True)
    belajar_kemampuan_intelektual = db.Column(db.String(5), nullable=True)
    pengendalian_perilaku    = db.Column(db.String(5), nullable=True)
    kesedihan_depresi        = db.Column(db.String(5), nullable=True)

    # Kesehatan
    kondisi_gizi             = db.Column(db.String(5),  nullable=True)
    penyakit_kronis          = db.Column(db.String(5),  nullable=True)

    # Bansos
    pbi_nas  = db.Column(db.String(5), nullable=True)
    pbi_pemda = db.Column(db.String(5), nullable=True)
    id_pelanggan_pln = db.Column(db.String(30), nullable=True)

    # Sync metadata
    provinsi_slug = db.Column(db.String(50), nullable=True, index=True)
    synced_at     = db.Column(db.DateTime, default=datetime.utcnow)
    raw_data      = db.Column(db.JSON, nullable=True)

    __table_args__ = (
        db.Index("idx_anggota_prov_nik", "provinsi_slug", "nomor_induk_kependudukan"),
    )

    @classmethod
    def from_api(cls, item: dict, provinsi_slug: str = None):
        return cls(
            nomor_induk_kependudukan        = str(item.get("nomor_induk_kependudukan") or ""),
            nomor_kartu_keluarga            = str(item.get("nomor_kartu_keluarga") or ""),
            nama                            = item.get("nama"),
            jenis_kelamin                   = str(item.get("jenis_kelamin") or ""),
            tanggal_lahir                   = _parse_date(item.get("tanggal_lahir")),
            status_kawin                    = str(item.get("status_kawin") or ""),
            status_hubungan_keluarga        = str(item.get("status_hubungan_keluarga") or ""),
            alamat_ktp                      = item.get("alamat_ktp"),
            dusun_ktp                       = item.get("dusun_ktp"),
            rt_ktp                          = str(item.get("rt_ktp") or ""),
            rw_ktp                          = str(item.get("rw_ktp") or ""),
            kelurahan_desa_ktp              = item.get("kelurahan_desa_ktp"),
            kecamatan_ktp                   = item.get("kecamatan_ktp"),
            kabupaten_kota_ktp              = item.get("kabupaten_kota_ktp"),
            provinsi_ktp                    = item.get("provinsi_ktp"),
            kode_kelurahan_desa_ktp         = item.get("kode_kelurahan_desa_ktp"),
            kode_kecamatan_ktp              = item.get("kode_kecamatan_ktp"),
            kode_kabupaten_kota_ktp         = item.get("kode_kabupaten_kota_ktp"),
            kode_provinsi_ktp               = item.get("kode_provinsi_ktp"),
            partisipasi_sekolah             = str(item.get("partisipasi_sekolah") or ""),
            jenjang_tertinggi_yang_diduduki = str(item.get("jenjang_tertinggi_yang_diduduki") or ""),
            kelas_tertinggi_yang_diduduki   = str(item.get("kelas_tertinggi_yang_diduduki") or ""),
            ijazah_tertinggi_yang_dimiliki  = str(item.get("ijazah_tertinggi_yang_dimiliki") or ""),
            status_bekerja                  = str(item.get("status_bekerja") or ""),
            status_dalam_pekerjaan_utama    = str(item.get("status_dalam_pekerjaan_utama") or ""),
            lapangan_usaha_dari_pekerjaan_utama = str(item.get("lapangan_usaha_dari_pekerjaan_utama") or ""),
            lapangan_usaha_dari_usaha_utama = str(item.get("lapangan_usaha_dari_usaha_utama") or ""),
            kepemilikan_usaha               = str(item.get("kepemilikan_usaha") or ""),
            jumlah_usaha                    = str(item.get("jumlah_usaha") or ""),
            omzet_usaha_utama               = str(item.get("omzet_usaha_utama") or ""),
            jumlah_pekerja_yang_dibayar_dari_usaha_utama        = str(item.get("jumlah_pekerja_yang_dibayar_dari_usaha_utama") or ""),
            jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama  = str(item.get("jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama") or ""),
            penglihatan                     = str(item.get("penglihatan") or ""),
            pendengaran                     = str(item.get("pendengaran") or ""),
            berjalan_atau_naik_tangga       = str(item.get("berjalan_atau_naik_tangga") or ""),
            menggunakan_tangan_jari         = str(item.get("menggunakan_tangan_jari") or ""),
            mengingat_berkonsentrasi        = str(item.get("mengingat_berkonsentrasi") or ""),
            mengurus_diri                   = str(item.get("mengurus_diri") or ""),
            berbicara_komunikasi            = str(item.get("berbicara_komunikasi") or ""),
            belajar_kemampuan_intelektual   = str(item.get("belajar_kemampuan_intelektual") or ""),
            pengendalian_perilaku           = str(item.get("pengendalian_perilaku") or ""),
            kesedihan_depresi               = str(item.get("kesedihan_depresi") or ""),
            kondisi_gizi                    = str(item.get("kondisi_gizi") or ""),
            penyakit_kronis                 = str(item.get("penyakit_kronis") or ""),
            pbi_nas                         = str(item.get("pbi_nas") or ""),
            pbi_pemda                       = str(item.get("pbi_pemda") or ""),
            id_pelanggan_pln                = str(item.get("id_pelanggan_pln") or ""),
            provinsi_slug                   = provinsi_slug,
            raw_data                        = item,
        )


class ZawaKeluarga(db.Model):
    __tablename__ = "zawa_keluarga"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # Identitas
    nomor_kartu_keluarga  = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nama_anggota_keluarga = db.Column(db.String(255), nullable=True)
    jumlah_anggota_keluarga = db.Column(db.Integer, nullable=True)

    # Alamat
    alamat             = db.Column(db.String(500), nullable=True)
    kelurahan_desa     = db.Column(db.String(100), nullable=True)
    kecamatan          = db.Column(db.String(100), nullable=True)
    kabupaten_kota     = db.Column(db.String(100), nullable=True)
    provinsi           = db.Column(db.String(100), nullable=True, index=True)
    kode_kelurahan_desa = db.Column(db.String(20), nullable=True)
    kode_kecamatan     = db.Column(db.String(20),  nullable=True)
    kode_kabupaten_kota = db.Column(db.String(20), nullable=True)
    kode_provinsi      = db.Column(db.String(5),   nullable=True)

    # Kondisi rumah
    luas_lantai             = db.Column(db.Float,  nullable=True)
    jenis_lantai_terluas    = db.Column(db.String(5), nullable=True)
    jenis_dinding_terluas   = db.Column(db.String(5), nullable=True)
    jenis_atap_terluas      = db.Column(db.String(5), nullable=True)
    jenis_kloset            = db.Column(db.String(5), nullable=True)
    fasilitas_bab           = db.Column(db.String(5), nullable=True)
    sumber_air_minum_utama  = db.Column(db.String(5), nullable=True)
    sumber_penerangan_utama = db.Column(db.String(5), nullable=True)
    bahan_bakar_utama_memasak = db.Column(db.String(5), nullable=True)
    daya_terpasang          = db.Column(db.String(5), nullable=True)
    pembuangan_akhir_tinja  = db.Column(db.String(5), nullable=True)
    status_kepemilikan_rumah = db.Column(db.String(5), nullable=True)
    kepemilikan_aset        = db.Column(db.String(5), nullable=True)

    # Aset bergerak
    aset_bergerak_sepeda_motor       = db.Column(db.String(5), nullable=True)
    aset_bergerak_mobil              = db.Column(db.String(5), nullable=True)
    aset_bergerak_sepeda             = db.Column(db.String(5), nullable=True)
    aset_bergerak_perahu             = db.Column(db.String(5), nullable=True)
    aset_bergerak_kapal_perahu_motor = db.Column(db.String(5), nullable=True)
    aset_bergerak_smartphone         = db.Column(db.String(5), nullable=True)
    aset_bergerak_komputer_laptop_tablet = db.Column(db.String(5), nullable=True)
    aset_bergerak_lemari_es          = db.Column(db.String(5), nullable=True)
    aset_bergerak_ac                 = db.Column(db.String(5), nullable=True)
    aset_bergerak_tv_datar           = db.Column(db.String(5), nullable=True)
    aset_bergerak_emas_perhiasan     = db.Column(db.String(5), nullable=True)
    aset_bergerak_tabung_gas         = db.Column(db.String(5), nullable=True)
    aset_bergerak_pemanas_air        = db.Column(db.String(5), nullable=True)
    aset_bergerak_telepon_rumah      = db.Column(db.String(5), nullable=True)

    # Aset tidak bergerak
    aset_tidak_bergerak_rumah_lainnya = db.Column(db.String(5), nullable=True)
    aset_tidak_bergerak_lahan_lainnya = db.Column(db.String(5), nullable=True)

    # Ternak
    jumlah_ternak_sapi          = db.Column(db.Integer, nullable=True)
    jumlah_ternak_kerbau        = db.Column(db.Integer, nullable=True)
    jumlah_ternak_kuda          = db.Column(db.Integer, nullable=True)
    jumlah_ternak_kambing_domba = db.Column(db.Integer, nullable=True)
    jumlah_ternak_babi          = db.Column(db.Integer, nullable=True)

    # Bansos & Ekonomi
    pbi_nas        = db.Column(db.String(5), nullable=True)
    pbi_pemda      = db.Column(db.String(5), nullable=True)
    desil_nasional = db.Column(db.String(5), nullable=True)
    id_pelanggan_pln = db.Column(db.String(30), nullable=True)

    # Sync metadata
    synced_at = db.Column(db.DateTime, default=datetime.utcnow)
    raw_data  = db.Column(db.JSON, nullable=True)

    @classmethod
    def from_api(cls, item: dict):
        def _s(v): return str(v) if v is not None else None
        def _i(v): return int(v) if v is not None else None
        def _f(v): return float(v) if v is not None else None

        return cls(
            nomor_kartu_keluarga             = _s(item.get("nomor_kartu_keluarga")),
            nama_anggota_keluarga            = item.get("nama_anggota_keluarga"),
            jumlah_anggota_keluarga          = _i(item.get("jumlah_anggota_keluarga")),
            alamat                           = item.get("alamat"),
            kelurahan_desa                   = item.get("kelurahan_desa"),
            kecamatan                        = item.get("kecamatan"),
            kabupaten_kota                   = item.get("kabupaten_kota"),
            provinsi                         = item.get("provinsi"),
            kode_kelurahan_desa              = item.get("kode_kelurahan_desa"),
            kode_kecamatan                   = item.get("kode_kecamatan"),
            kode_kabupaten_kota              = item.get("kode_kabupaten_kota"),
            kode_provinsi                    = item.get("kode_provinsi"),
            luas_lantai                      = _f(item.get("luas_lantai")),
            jenis_lantai_terluas             = _s(item.get("jenis_lantai_terluas")),
            jenis_dinding_terluas            = _s(item.get("jenis_dinding_terluas")),
            jenis_atap_terluas               = _s(item.get("jenis_atap_terluas")),
            jenis_kloset                     = _s(item.get("jenis_kloset")),
            fasilitas_bab                    = _s(item.get("fasilitas_bab")),
            sumber_air_minum_utama           = _s(item.get("sumber_air_minum_utama")),
            sumber_penerangan_utama          = _s(item.get("sumber_penerangan_utama")),
            bahan_bakar_utama_memasak        = _s(item.get("bahan_bakar_utama_memasak")),
            daya_terpasang                   = _s(item.get("daya_terpasang")),
            pembuangan_akhir_tinja           = _s(item.get("pembuangan_akhir_tinja")),
            status_kepemilikan_rumah         = _s(item.get("status_kepemilikan_rumah")),
            kepemilikan_aset                 = _s(item.get("kepemilikan_aset")),
            aset_bergerak_sepeda_motor       = _s(item.get("aset_bergerak_sepeda_motor")),
            aset_bergerak_mobil              = _s(item.get("aset_bergerak_mobil")),
            aset_bergerak_sepeda             = _s(item.get("aset_bergerak_sepeda")),
            aset_bergerak_perahu             = _s(item.get("aset_bergerak_perahu")),
            aset_bergerak_kapal_perahu_motor = _s(item.get("aset_bergerak_kapal_perahu_motor")),
            aset_bergerak_smartphone         = _s(item.get("aset_bergerak_smartphone")),
            aset_bergerak_komputer_laptop_tablet = _s(item.get("aset_bergerak_komputer_laptop_tablet")),
            aset_bergerak_lemari_es          = _s(item.get("aset_bergerak_lemari_es")),
            aset_bergerak_ac                 = _s(item.get("aset_bergerak_ac")),
            aset_bergerak_tv_datar           = _s(item.get("aset_bergerak_tv_datar")),
            aset_bergerak_emas_perhiasan     = _s(item.get("aset_bergerak_emas_perhiasan")),
            aset_bergerak_tabung_gas         = _s(item.get("aset_bergerak_tabung_gas")),
            aset_bergerak_pemanas_air        = _s(item.get("aset_bergerak_pemanas_air")),
            aset_bergerak_telepon_rumah      = _s(item.get("aset_bergerak_telepon_rumah")),
            aset_tidak_bergerak_rumah_lainnya = _s(item.get("aset_tidak_bergerak_rumah_lainnya")),
            aset_tidak_bergerak_lahan_lainnya = _s(item.get("aset_tidak_bergerak_lahan_lainnya")),
            jumlah_ternak_sapi               = _i(item.get("jumlah_ternak_sapi")),
            jumlah_ternak_kerbau             = _i(item.get("jumlah_ternak_kerbau")),
            jumlah_ternak_kuda               = _i(item.get("jumlah_ternak_kuda")),
            jumlah_ternak_kambing_domba      = _i(item.get("jumlah_ternak_kambing_domba")),
            jumlah_ternak_babi               = _i(item.get("jumlah_ternak_babi")),
            pbi_nas                          = _s(item.get("pbi_nas")),
            pbi_pemda                        = _s(item.get("pbi_pemda")),
            desil_nasional                   = _s(item.get("desil_nasional")),
            id_pelanggan_pln                 = _s(item.get("id_pelanggan_pln")),
            raw_data                         = item,
        )


class ZawaSyncLog(db.Model):
    __tablename__ = "zawa_sync_log"

    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sync_type      = db.Column(db.String(50),   nullable=False)
    status         = db.Column(db.String(20),   nullable=False, default="pending")
    total_fetched  = db.Column(db.Integer,      nullable=True, default=0)
    total_saved    = db.Column(db.Integer,      nullable=True, default=0)
    error_message  = db.Column(db.Text,         nullable=True)
    started_at     = db.Column(db.DateTime,     default=datetime.utcnow)
    finished_at    = db.Column(db.DateTime,     nullable=True)
