from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.zawa import ZawaSyncLog
from app.services.zawa_sync import (
    start_sync_anggota,
    start_sync_keluarga,
    get_running_jobs,
)
from flask import current_app

sync_bp = Blueprint("sync", __name__, url_prefix="/baseline/sync")


@sync_bp.post("/anggota")
@jwt_required()
def sync_anggota():
    """Mulai background sync anggota untuk 1 provinsi.
    Body JSON: { "provinsi": "aceh" }
    """
    body     = request.get_json(silent=True) or {}
    provinsi = (body.get("provinsi") or "").strip().lower()

    if not provinsi:
        return jsonify({"success": False, "message": "provinsi wajib diisi"}), 400

    result = start_sync_anggota(current_app._get_current_object(), provinsi)

    if result["status"] == "already_running":
        return jsonify({
            "success": False,
            "message": f"Sync anggota provinsi '{provinsi}' sedang berjalan.",
            "data": result
        }), 409

    return jsonify({
        "success": True,
        "message": f"Sync anggota provinsi '{provinsi}' dimulai di background.",
        "data": result
    }), 202


@sync_bp.post("/keluarga")
@jwt_required()
def sync_keluarga():
    """Mulai background sync keluarga (global, max 50rb baris)."""
    result = start_sync_keluarga(current_app._get_current_object())

    if result["status"] == "already_running":
        return jsonify({
            "success": False,
            "message": "Sync keluarga sedang berjalan.",
            "data": result
        }), 409

    return jsonify({
        "success": True,
        "message": "Sync keluarga dimulai di background.",
        "data": result
    }), 202


@sync_bp.get("/status")
@jwt_required()
def sync_status():
    """Lihat 20 log sync terakhir + job yang sedang berjalan."""
    logs = (
        ZawaSyncLog.query
        .order_by(ZawaSyncLog.started_at.desc())
        .limit(20)
        .all()
    )

    return jsonify({
        "success": True,
        "data": {
            "running_jobs": get_running_jobs(),
            "logs": [
                {
                    "id":            l.id,
                    "sync_type":     l.sync_type,
                    "status":        l.status,
                    "total_fetched": l.total_fetched,
                    "total_saved":   l.total_saved,
                    "started_at":    str(l.started_at),
                    "finished_at":   str(l.finished_at) if l.finished_at else None,
                    "error_message": l.error_message,
                }
                for l in logs
            ]
        }
    })


@sync_bp.post("/resume/anggota")
@jwt_required()
def resume_anggota():
    """Resume sync anggota yang gagal di tengah jalan (cursor tersimpan).
    Body JSON: { "provinsi": "aceh", "sync_log_id": 5 }
    """
    body         = request.get_json(silent=True) or {}
    provinsi     = (body.get("provinsi") or "").strip().lower()
    sync_log_id  = body.get("sync_log_id")

    if not provinsi or not sync_log_id:
        return jsonify({"success": False, "message": "provinsi dan sync_log_id wajib"}), 400

    result = start_sync_anggota(
        current_app._get_current_object(), provinsi
    )

    return jsonify({
        "success": True,
        "message": f"Resume sync anggota '{provinsi}' dimulai.",
        "data": result
    }), 202
