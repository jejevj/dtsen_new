from ..extensions import db
from datetime import datetime


class Laz(db.Model):
    """
    Model untuk tabel t_laz.
    Menyimpan data Lembaga Amil Zakat (LAZ) beserta cabang/unit layanannya.
    """
    __tablename__ = 't_laz'

    laz_id                       = db.Column(db.Integer,      primary_key=True, autoincrement=True)
    iduser                       = db.Column(db.Integer,      nullable=False)
    pp_kode                      = db.Column(db.String(10),   nullable=True)
    laz_kode                     = db.Column(db.String(50),   nullable=True, index=True)
    laz_parent_kode              = db.Column(db.String(50),   nullable=True, index=True)
    laz_nama                     = db.Column(db.String(255),  nullable=True)
    laz_badan_hukum_nama         = db.Column(db.String(255),  nullable=True)
    pranala                      = db.Column(db.String(255),  nullable=True)
    x_url                        = db.Column(db.String(500),  nullable=True)
    youtube_url                  = db.Column(db.String(500),  nullable=True)
    instagram_url                = db.Column(db.String(500),  nullable=True)
    facebook_url                 = db.Column(db.String(1000), nullable=True)
    skala                        = db.Column(db.Integer,      nullable=True, default=0)
    alamat_kantor                = db.Column(db.String(255),  nullable=True)
    alamat_rt                    = db.Column(db.String(10),   nullable=True)
    alamat_rw                    = db.Column(db.String(10),   nullable=True)
    alamat_no                    = db.Column(db.String(10),   nullable=True)
    provinsi_kode                = db.Column(db.String(2),    nullable=True)
    kabkota_kode                 = db.Column(db.String(4),    nullable=True)
    kecamatan_kode               = db.Column(db.String(6),    nullable=True)
    kelurahan_kode               = db.Column(db.String(10),   nullable=True)
    mustahik_jumlah              = db.Column(db.Integer,      nullable=True, default=0)
    muzakki_jumlah               = db.Column(db.Integer,      nullable=True, default=0)
    laz_tipe                     = db.Column(
        db.Enum('pusat', 'perwakilan', 'unit layanan'),
        nullable=False,
        default='pusat'
    )
    laz_status                   = db.Column(
        db.Enum(
            'usul', 'aktif', 'daftar hitam', 'inaktif',
            'daftar_ulang', 'verified', 'none', 'expired'
        ),
        nullable=False,
        default='usul',
        index=True
    )
    is_daftar_ulang              = db.Column(db.String(1),    nullable=True, default='0')
    is_perwakilan_daftar_ulang   = db.Column(db.String(1),    nullable=True, default='0')
    laz_catatan                  = db.Column(db.Text,         nullable=True)
    usulan_ref_id                = db.Column(db.Integer,      nullable=True)
    created_at                   = db.Column(db.DateTime,     nullable=False, default=datetime.utcnow)
    updated_at                   = db.Column(db.DateTime,     nullable=True)

    # Relasi ke akses dtsen berdasarkan laz_kode
    dtsen_akses = db.relationship(
        'TDtsenAkses',
        primaryjoin='foreign(TDtsenAkses.laz_kode) == Laz.laz_kode',
        backref='laz',
        lazy='dynamic',
        viewonly=True
    )

    def __repr__(self):
        return f'<Laz {self.laz_kode} [{self.laz_tipe}] {self.laz_nama}>'

    def to_dict(self):
        return {
            'laz_id':                     self.laz_id,
            'iduser':                     self.iduser,
            'pp_kode':                    self.pp_kode,
            'laz_kode':                   self.laz_kode,
            'laz_parent_kode':            self.laz_parent_kode,
            'laz_nama':                   self.laz_nama,
            'laz_badan_hukum_nama':       self.laz_badan_hukum_nama,
            'pranala':                    self.pranala,
            'x_url':                      self.x_url,
            'youtube_url':                self.youtube_url,
            'instagram_url':              self.instagram_url,
            'facebook_url':               self.facebook_url,
            'skala':                      self.skala,
            'alamat_kantor':              self.alamat_kantor,
            'alamat_rt':                  self.alamat_rt,
            'alamat_rw':                  self.alamat_rw,
            'alamat_no':                  self.alamat_no,
            'provinsi_kode':              self.provinsi_kode,
            'kabkota_kode':               self.kabkota_kode,
            'kecamatan_kode':             self.kecamatan_kode,
            'kelurahan_kode':             self.kelurahan_kode,
            'mustahik_jumlah':            self.mustahik_jumlah,
            'muzakki_jumlah':             self.muzakki_jumlah,
            'laz_tipe':                   self.laz_tipe,
            'laz_status':                 self.laz_status,
            'is_daftar_ulang':            self.is_daftar_ulang,
            'is_perwakilan_daftar_ulang': self.is_perwakilan_daftar_ulang,
            'laz_catatan':                self.laz_catatan,
            'usulan_ref_id':              self.usulan_ref_id,
            'created_at':                 self.created_at.isoformat() if self.created_at else None,
            'updated_at':                 self.updated_at.isoformat() if self.updated_at else None,
        }
