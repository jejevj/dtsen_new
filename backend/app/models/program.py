from ..extensions import db


class Bidang(db.Model):
    __tablename__ = 'm_bidang'

    bidang_kode = db.Column(db.String(20), primary_key=True)
    bidang_label = db.Column(db.String(100), nullable=False)

    programs = db.relationship('Program', backref='bidang', lazy='dynamic')


class Program(db.Model):
    __tablename__ = 't_program'

    program_kode = db.Column(db.String(50), primary_key=True)
    program_nama = db.Column(db.String(255), nullable=False)
    bidang_kode = db.Column(db.String(20), db.ForeignKey('m_bidang.bidang_kode'), nullable=True)

    def __repr__(self):
        return f'<Program {self.program_kode} - {self.program_nama}>'
