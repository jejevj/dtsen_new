from flask import request, jsonify
from . import api_v1_bp
from ...models.wilayah import Provinsi, KabKota, Kecamatan, Kelurahan


@api_v1_bp.get('/wilayah/provinsi')
def list_provinsi():
    data = Provinsi.query.order_by(Provinsi.provinsi_nama).all()
    return jsonify([{'kode': p.provinsi_kode, 'nama': p.provinsi_nama} for p in data]), 200


@api_v1_bp.get('/wilayah/kabkota')
def list_kabkota():
    data = KabKota.query.order_by(KabKota.kabkota_nama).all()
    return jsonify([{'kode': k.kabkota_kode, 'nama': k.kabkota_nama} for k in data]), 200


@api_v1_bp.get('/wilayah/kecamatan')
def list_kecamatan():
    data = Kecamatan.query.order_by(Kecamatan.kecamatan_nama).all()
    return jsonify([{'kode': k.kecamatan_kode, 'nama': k.kecamatan_nama} for k in data]), 200


@api_v1_bp.get('/wilayah/kelurahan')
def list_kelurahan():
    data = Kelurahan.query.order_by(Kelurahan.kelurahan_nama).all()
    return jsonify([{'kode': k.kelurahan_kode, 'nama': k.kelurahan_nama} for k in data]), 200
