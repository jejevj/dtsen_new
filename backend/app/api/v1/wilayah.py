import logging
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from . import api_v1_bp
from ...extensions import db
from ...models.wilayah import Provinsi, KabKota, Kecamatan
from ...models.wilayah import Provinsi, KabKota, Kecamatan, Kelurahan
from ...models.t_dtsen_akses import TDtsenAkses
from ...models.t_dtsen_wilayah import TDtsenWilayah
from ...services.auth_service import parse_identity_str
from flask_jwt_extended import get_jwt_identity

logger = logging.getLogger('app')


# ─── Identity helper ──────────────────────────────────────────

def _identity() -> dict:
    return parse_identity_str(get_jwt_identity())

def _is_tuser(identity: dict) -> bool:
    return identity.get('type') in ('tuser', 'admin', 'user')

def _get_dtsen_akses(identity: dict) -> TDtsenAkses | None:
    if _is_tuser(identity):
        return None
    return TDtsenAkses.query.filter_by(dtsen_akses_id=identity.get('id')).first()


# ─── Skala helper ─────────────────────────────────────────────
# Skala LAZ:
#   1 = Nasional  → dropdown: semua provinsi, semua kabkota, semua kecamatan
#   2 = Provinsi  → dropdown: provinsi terkait, kabkota di bawahnya, kecamatan di bawahnya
#   3 = Kabkota   → dropdown: kabkota terkait, kecamatan di bawahnya

def _wilayah_rows(dtsen_akses_id) -> list[TDtsenWilayah]:
    return TDtsenWilayah.query.filter_by(dtsen_akses_id=dtsen_akses_id).all()


# ─── Endpoints ────────────────────────────────────────────────

@api_v1_bp.get('/wilayah/dropdown')
@jwt_required()
def wilayah_dropdown():
    """
    Kembalikan opsi dropdown wilayah sesuai skala akses user.

    Query params (opsional, untuk drilldown dinamis):
      provinsi_kode  — filter kabkota berdasarkan provinsi
      kabkota_kode   — filter kecamatan berdasarkan kabkota

    Response:
    {
      "skala": 1,
      "skala_label": "nasional",
      "provinsi": [{"kode": "11", "nama": "Aceh"}, ...],
      "kabkota":  [{"kode": "1101", "nama": "...", "provinsi_kode": "11"}, ...],
      "kecamatan": [{"kode": "110101", "nama": "...", "kabkota_kode": "1101"}, ...]
    }
    """
    identity = _identity()
    provinsi_filter  = request.args.get('provinsi_kode', '').strip() or None
    kabkota_filter   = request.args.get('kabkota_kode', '').strip() or None

    # ── Superadmin / tuser: akses penuh nasional ──────────────
    if _is_tuser(identity):
        return _build_nasional(provinsi_filter, kabkota_filter)

    # ── LAZ user ──────────────────────────────────────────────
    dtsen = _get_dtsen_akses(identity)
    if dtsen is None:
        return jsonify({"error": "Data akses tidak ditemukan."}), 403

    skala = dtsen.laz_skala or 0
    rows  = _wilayah_rows(dtsen.dtsen_akses_id)

    if skala == 1:  # Nasional
        return _build_nasional(provinsi_filter, kabkota_filter)

    elif skala == 2:  # Provinsi
        allowed_prov = list({r.provinsi_kode for r in rows if r.provinsi_kode})
        return _build_provinsi_scope(allowed_prov, provinsi_filter, kabkota_filter)

    elif skala == 3:  # Kabkota
        allowed_kab = list({r.kabkota_kode for r in rows if r.kabkota_kode})
        # Provinsi unik dari kabkota yang diizinkan
        allowed_prov = list({r.provinsi_kode for r in rows if r.provinsi_kode})
        return _build_kabkota_scope(allowed_prov, allowed_kab, kabkota_filter)

    return jsonify({"error": f"Skala LAZ '{skala}' tidak dikenal."}), 400


# ─── Builder functions ────────────────────────────────────────

def _build_nasional(provinsi_filter, kabkota_filter):
    """Skala 1: semua provinsi, semua kabkota, semua kecamatan."""
    # Provinsi
    prov_q = Provinsi.query.filter_by(provinsi_aktif='y').order_by(Provinsi.provinsi_nama)
    provinsi_list = [
        {"kode": p.provinsi_kode, "nama": p.provinsi_nama}
        for p in prov_q.all()
    ]

    # Kabkota — filter by provinsi jika ada query param
    kab_q = KabKota.query.filter_by(kabkota_aktif='y').order_by(KabKota.kabkota_nama)
    if provinsi_filter:
        kab_q = kab_q.filter_by(provinsi_kode=provinsi_filter)
    kabkota_list = [
        {"kode": k.kabkota_kode, "nama": k.kabkota_nama, "provinsi_kode": k.provinsi_kode}
        for k in kab_q.all()
    ]

    # Kecamatan — filter by kabkota jika ada query param
    kec_q = Kecamatan.query.filter_by(kecamatan_aktif='y').order_by(Kecamatan.kecamatan_nama)
    if kabkota_filter:
        kec_q = kec_q.filter_by(kabkota_kode=kabkota_filter)
    elif provinsi_filter:
        # Kecamatan di semua kabkota yang termasuk provinsi ini
        kab_kode_list = [k["kode"] for k in kabkota_list]
        kec_q = kec_q.filter(Kecamatan.kabkota_kode.in_(kab_kode_list))
    kecamatan_list = [
        {"kode": k.kecamatan_kode, "nama": k.kecamatan_nama, "kabkota_kode": k.kabkota_kode}
        for k in kec_q.all()
    ]

    return jsonify({
        "skala": 1,
        "skala_label": "nasional",
        "provinsi":  provinsi_list,
        "kabkota":   kabkota_list,
        "kecamatan": kecamatan_list,
    }), 200


def _build_provinsi_scope(allowed_prov: list, provinsi_filter, kabkota_filter):
    """Skala 2: hanya provinsi yang diizinkan beserta hierarkinya."""
    # Provinsi
    prov_q = Provinsi.query.filter(
        Provinsi.provinsi_kode.in_(allowed_prov),
        Provinsi.provinsi_aktif == 'y'
    ).order_by(Provinsi.provinsi_nama)
    provinsi_list = [
        {"kode": p.provinsi_kode, "nama": p.provinsi_nama}
        for p in prov_q.all()
    ]

    # Tentukan provinsi aktif untuk filter kabkota
    active_prov = provinsi_filter if (provinsi_filter and provinsi_filter in allowed_prov) \
        else (allowed_prov[0] if len(allowed_prov) == 1 else None)

    kab_q = KabKota.query.filter(
        KabKota.provinsi_kode.in_(allowed_prov),
        KabKota.kabkota_aktif == 'y'
    ).order_by(KabKota.kabkota_nama)
    if active_prov:
        kab_q = kab_q.filter_by(provinsi_kode=active_prov)
    kabkota_list = [
        {"kode": k.kabkota_kode, "nama": k.kabkota_nama, "provinsi_kode": k.provinsi_kode}
        for k in kab_q.all()
    ]

    kec_q = Kecamatan.query.filter_by(kecamatan_aktif='y').order_by(Kecamatan.kecamatan_nama)
    if kabkota_filter:
        kec_q = kec_q.filter_by(kabkota_kode=kabkota_filter)
    else:
        kab_kode_list = [k["kode"] for k in kabkota_list]
        kec_q = kec_q.filter(Kecamatan.kabkota_kode.in_(kab_kode_list)) if kab_kode_list \
            else kec_q.filter(db.false())
    kecamatan_list = [
        {"kode": k.kecamatan_kode, "nama": k.kecamatan_nama, "kabkota_kode": k.kabkota_kode}
        for k in kec_q.all()
    ]

    return jsonify({
        "skala": 2,
        "skala_label": "provinsi",
        "provinsi":  provinsi_list,
        "kabkota":   kabkota_list,
        "kecamatan": kecamatan_list,
    }), 200


def _build_kabkota_scope(allowed_prov: list, allowed_kab: list, kabkota_filter):
    """Skala 3: hanya kabkota yang diizinkan beserta kecamatannya."""
    # Provinsi (sebagai info/label saja, tidak bisa dipilih lain)
    prov_q = Provinsi.query.filter(
        Provinsi.provinsi_kode.in_(allowed_prov),
        Provinsi.provinsi_aktif == 'y'
    ).order_by(Provinsi.provinsi_nama)
    provinsi_list = [
        {"kode": p.provinsi_kode, "nama": p.provinsi_nama}
        for p in prov_q.all()
    ]

    # Kabkota
    kab_q = KabKota.query.filter(
        KabKota.kabkota_kode.in_(allowed_kab),
        KabKota.kabkota_aktif == 'y'
    ).order_by(KabKota.kabkota_nama)
    kabkota_list = [
        {"kode": k.kabkota_kode, "nama": k.kabkota_nama, "provinsi_kode": k.provinsi_kode}
        for k in kab_q.all()
    ]

    # Kecamatan
    active_kab = kabkota_filter if (kabkota_filter and kabkota_filter in allowed_kab) \
        else (allowed_kab[0] if len(allowed_kab) == 1 else None)
    kec_q = Kecamatan.query.filter(
        Kecamatan.kabkota_kode.in_(allowed_kab),
        Kecamatan.kecamatan_aktif == 'y'
    ).order_by(Kecamatan.kecamatan_nama)
    if active_kab:
        kec_q = kec_q.filter_by(kabkota_kode=active_kab)
    kecamatan_list = [
        {"kode": k.kecamatan_kode, "nama": k.kecamatan_nama, "kabkota_kode": k.kabkota_kode}
        for k in kec_q.all()
    ]

    return jsonify({
        "skala": 3,
        "skala_label": "kabkota",
        "provinsi":  provinsi_list,
        "kabkota":   kabkota_list,
        "kecamatan": kecamatan_list,
    }), 200


@api_v1_bp.get('/wilayah/provinsi')
@jwt_required()
def wilayah_provinsi():
    """Shortcut: hanya list provinsi sesuai akses."""
    identity = _identity()

    if _is_tuser(identity):
        rows = Provinsi.query.filter_by(provinsi_aktif='y').order_by(Provinsi.provinsi_nama).all()
    else:
        dtsen = _get_dtsen_akses(identity)
        if dtsen is None:
            return jsonify({"error": "Data akses tidak ditemukan."}), 403
        rows_wilayah = _wilayah_rows(dtsen.dtsen_akses_id)
        allowed_prov = list({r.provinsi_kode for r in rows_wilayah if r.provinsi_kode})
        if dtsen.laz_skala == 1:  # Nasional
            rows = Provinsi.query.filter_by(provinsi_aktif='y').order_by(Provinsi.provinsi_nama).all()
        else:
            rows = Provinsi.query.filter(
                Provinsi.provinsi_kode.in_(allowed_prov),
                Provinsi.provinsi_aktif == 'y'
            ).order_by(Provinsi.provinsi_nama).all()

    return jsonify({
        "data": [{"kode": p.provinsi_kode, "nama": p.provinsi_nama} for p in rows]
    }), 200


@api_v1_bp.get('/wilayah/kabkota')
@jwt_required()
def wilayah_kabkota():
    """Kabkota berdasarkan provinsi_kode (query param)."""
    provinsi_kode = request.args.get('provinsi_kode', '').strip()
    if not provinsi_kode:
        return jsonify({"error": "provinsi_kode wajib diisi."}), 400

    identity = _identity()

    if _is_tuser(identity):
        rows = KabKota.query.filter_by(
            provinsi_kode=provinsi_kode, kabkota_aktif='y'
        ).order_by(KabKota.kabkota_nama).all()
    else:
        dtsen = _get_dtsen_akses(identity)
        if dtsen is None:
            return jsonify({"error": "Data akses tidak ditemukan."}), 403
        rows_wilayah = _wilayah_rows(dtsen.dtsen_akses_id)
        skala = dtsen.laz_skala or 0

        q = KabKota.query.filter_by(provinsi_kode=provinsi_kode, kabkota_aktif='y')
        if skala == 1:  # Nasional — semua
            rows = q.order_by(KabKota.kabkota_nama).all()
        elif skala == 2:  # Provinsi — semua kabkota di provinsi itu
            allowed_prov = {r.provinsi_kode for r in rows_wilayah if r.provinsi_kode}
            if provinsi_kode not in allowed_prov:
                return jsonify({"error": "Akses ditolak untuk provinsi ini."}), 403
            rows = q.order_by(KabKota.kabkota_nama).all()
        else:  # Kabkota — hanya yang diizinkan
            allowed_kab = {r.kabkota_kode for r in rows_wilayah if r.kabkota_kode}
            rows = q.filter(KabKota.kabkota_kode.in_(allowed_kab)).order_by(KabKota.kabkota_nama).all()

    return jsonify({
        "data": [
            {"kode": k.kabkota_kode, "nama": k.kabkota_nama, "provinsi_kode": k.provinsi_kode}
            for k in rows
        ]
    }), 200


@api_v1_bp.get('/wilayah/kecamatan')
@jwt_required()
def wilayah_kecamatan():
    """Kecamatan berdasarkan kabkota_kode (query param)."""
    kabkota_kode = request.args.get('kabkota_kode', '').strip()
    if not kabkota_kode:
        return jsonify({"error": "kabkota_kode wajib diisi."}), 400

    identity = _identity()

    if _is_tuser(identity):
        rows = Kecamatan.query.filter_by(
            kabkota_kode=kabkota_kode, kecamatan_aktif='y'
        ).order_by(Kecamatan.kecamatan_nama).all()
    else:
        dtsen = _get_dtsen_akses(identity)
        if dtsen is None:
            return jsonify({"error": "Data akses tidak ditemukan."}), 403
        rows_wilayah = _wilayah_rows(dtsen.dtsen_akses_id)
        skala = dtsen.laz_skala or 0

        q = Kecamatan.query.filter_by(kabkota_kode=kabkota_kode, kecamatan_aktif='y')
        if skala in (1, 2):  # Nasional atau Provinsi — semua kecamatan
            rows = q.order_by(Kecamatan.kecamatan_nama).all()
        else:  # Kabkota — hanya kabkota yang diizinkan
            allowed_kab = {r.kabkota_kode for r in rows_wilayah if r.kabkota_kode}
            if kabkota_kode not in allowed_kab:
                return jsonify({"error": "Akses ditolak untuk kabkota ini."}), 403
            rows = q.order_by(Kecamatan.kecamatan_nama).all()

    return jsonify({
        "data": [
            {"kode": k.kecamatan_kode, "nama": k.kecamatan_nama, "kabkota_kode": k.kabkota_kode}
            for k in rows
        ]
    }), 200

@api_v1_bp.get('/wilayah/kelurahan')
@jwt_required()
def wilayah_kelurahan():
    """Kelurahan berdasarkan kecamatan_kode."""

    kecamatan_kode = request.args.get('kecamatan_kode', '').strip()

    if not kecamatan_kode:
        return jsonify({"error": "kecamatan_kode wajib diisi."}), 400

    rows = (
        Kelurahan.query
        .filter_by(
            kecamatan_kode=kecamatan_kode
        )
        .order_by(Kelurahan.kelurahan_nama)
        .all()
    )

    return jsonify({
        "data": [
            {
                "kode": k.kelurahan_kode,
                "nama": k.kelurahan_nama,
                "kecamatan_kode": k.kecamatan_kode
            }
            for k in rows
        ]
    }), 200
