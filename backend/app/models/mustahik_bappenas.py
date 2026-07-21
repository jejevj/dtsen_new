from ..extensions import db

class MustahikBappenas(db.Model):
    __tablename__ = "t_mustahik_bappenas"

    nik = db.Column(db.String(16), primary_key=True)
    desil = db.Column(db.Integer)

    def __repr__(self):
        return f"<MustahikBappenas {self.nik}>"