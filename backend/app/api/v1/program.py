from flask import jsonify
from . import api_v1_bp
from ...models.program import Program


@api_v1_bp.get('/program')
def list_program():
    """List seluruh program."""

    data = (
        Program.query
        .order_by(Program.program_nama.asc())
        .all()
    )

    return jsonify([
        {
            "program_kode": p.program_kode,
            "program_nama": p.program_nama,
            "bidang_kode": p.bidang_kode
        }
        for p in data
    ]), 200