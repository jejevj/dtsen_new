import hashlib
from ..models.mustahik import Mustahik
from ..schemas.mustahik import MustahikSchema
from ..extensions import db

mustahik_schema = MustahikSchema()
mustahiks_schema = MustahikSchema(many=True)


class MustahikService:
    @staticmethod
    def get_list(params: dict) -> dict:
        query = Mustahik.query

        if params.get('nama'):
            query = query.filter(Mustahik.nama_lengkap.ilike(f"%{params['nama']}%"))
        if params.get('nik'):
            query = query.filter_by(nik=int(params['nik']))
        if params.get('jenis_kelamin'):
            query = query.filter_by(jenis_kelamin=params['jenis_kelamin'])
        if params.get('agama'):
            query = query.filter_by(agama=params['agama'])
        if params.get('laz_kode'):
            query = query.filter_by(laz_kode=params['laz_kode'])
        if params.get('program_kode'):
            query = query.filter_by(program_kode=params['program_kode'])

        page = int(params.get('page', 1))
        per_page = int(params.get('per_page', 20))
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'data': mustahiks_schema.dump(paginated.items),
            'meta': {
                'page': paginated.page,
                'per_page': paginated.per_page,
                'total': paginated.total,
                'pages': paginated.pages,
            }
        }

    @staticmethod
    def get_detail(nik_hashed: str) -> dict:
        all_mustahik = Mustahik.query.all()
        match = [
            m for m in all_mustahik
            if hashlib.md5(str(m.nik).encode()).hexdigest() == nik_hashed
        ]
        if not match:
            return {'message': 'Data tidak ditemukan.', 'status_code': 404}
        return {'data': mustahiks_schema.dump(match)}
