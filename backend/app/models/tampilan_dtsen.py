from ..extensions import db


class TampilanDtsen(db.Model):
    """Master konfigurasi field/kolom tampilan data sensus DTSEN."""
    __tablename__ = 'm_tampilan_dtsen'

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    field_key   = db.Column(db.String(100), nullable=False, unique=True,
                            comment='Nama key dari API DTSEN, unik')
    field_label = db.Column(db.String(200), nullable=False,
                            comment='Label kolom yang ditampilkan ke user')
    field_group = db.Column(db.String(100), nullable=False, default='',
                            comment='Grup/seksi field (cth: Identitas, Pendidikan)')
    kategori    = db.Column(db.Enum('individu', 'keluarga'), nullable=False, default='individu')
    field_type  = db.Column(db.String(50), nullable=False, default='String',
                            comment='String, String (kode), Integer, Float, Date')
    is_filter   = db.Column(db.SmallInteger, nullable=False, default=0,
                            comment='1 = bisa dijadikan filter pencarian')
    is_detail   = db.Column(db.SmallInteger, nullable=False, default=0,
                            comment='1 = tampil di halaman detail individu')
    is_active   = db.Column(db.SmallInteger, nullable=False, default=1)
    urutan      = db.Column(db.Integer, nullable=False, default=0,
                            comment='Urutan tampil kolom')

    # Relasi ke referensi kode
    refs = db.relationship(
        'TampilanDtsenRef',
        backref='tampilan',
        lazy='dynamic',
        cascade='all, delete-orphan',
        order_by='TampilanDtsenRef.urutan'
    )

    def to_dict(self, with_refs=False):
        d = {
            'id':          self.id,
            'field_key':   self.field_key,
            'field_label': self.field_label,
            'field_group': self.field_group,
            'kategori':    self.kategori,
            'field_type':  self.field_type,
            'is_filter':   self.is_filter,
            'is_detail':   self.is_detail,
            'urutan':      self.urutan,
        }
        if with_refs:
            d['refs'] = [r.to_dict() for r in self.refs.all()]
        return d

    def __repr__(self):
        return f'<TampilanDtsen {self.field_key}>'


class TampilanDtsenRef(db.Model):
    """Referensi kode → keterangan per field tampilan DTSEN."""
    __tablename__ = 'm_tampilan_dtsen_ref'

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tampilan_id = db.Column(db.Integer, db.ForeignKey(
                      'm_tampilan_dtsen.id', ondelete='CASCADE', onupdate='CASCADE'),
                      nullable=False, comment='FK ke m_tampilan_dtsen.id')
    ref_value   = db.Column(db.String(50), nullable=False,
                            comment='Nilai/kode dari API (cth: 1, 01, 0)')
    ref_label   = db.Column(db.String(200), nullable=False,
                            comment='Keterangan nilai (cth: Laki-laki)')
    urutan      = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (
        db.UniqueConstraint('tampilan_id', 'ref_value', name='uq_tampilan_ref_value'),
    )

    def to_dict(self):
        return {
            'id':        self.id,
            'ref_value': self.ref_value,
            'ref_label': self.ref_label,
            'urutan':    self.urutan,
        }

    def __repr__(self):
        return f'<TampilanDtsenRef {self.tampilan_id}:{self.ref_value}>'
