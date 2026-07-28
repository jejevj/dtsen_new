from app.extensions import db
from datetime import datetime


class IcOptions(db.Model):
    """Model untuk tabel ic_options — key-value store konfigurasi aplikasi."""
    __tablename__ = "ic_options"

    id_options = db.Column(db.Integer, primary_key=True, autoincrement=True)
    opt_name   = db.Column(db.String(255), nullable=False, unique=True, index=True)
    opt_values = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=True,
                           onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f"<IcOptions {self.opt_name}={self.opt_values}>"

    @classmethod
    def get(cls, name: str) -> "IcOptions | None":
        """Ambil satu row berdasarkan opt_name."""
        return cls.query.filter_by(opt_name=name).first()

    @classmethod
    def get_value(cls, name: str, default=None) -> str | None:
        """Ambil nilai opt_values langsung, atau default jika tidak ditemukan."""
        row = cls.get(name)
        return row.opt_values if row else default
