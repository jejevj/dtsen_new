import api from './api'

const PUBLIC = '/public/report'

export default {
  // ── Public (no auth) ────────────────────────────────────────────────────
  getParamTahun:   (params) => api.get(`${PUBLIC}/paramtahun`,{ params }).then(r => r.data),
  getSummary:      (params) => api.get(`${PUBLIC}/summary`,   { params }).then(r => r.data),
  getGender:       (params) => api.get(`${PUBLIC}/gender`,    { params }).then(r => r.data),
  getBidang:       (params) => api.get(`${PUBLIC}/bidang`,    { params }).then(r => r.data),
  getTimeseries:   (params) => api.get(`${PUBLIC}/timeseries`,{ params }).then(r => r.data),
  getSkalaLaz:     (params) => api.get(`${PUBLIC}/skala-laz`, { params }).then(r => r.data),

  // ── Public Maps ────────────────────────────────────────────────────────── 
  getMapData:         (tahun)                => api.get(`${PUBLIC}/map`, { params: { tahun } }).then(r => r.data),
  getMapDataKabkota:  (tahun, provinsi_kode) => api.get(`${PUBLIC}/map`, { params: { tahun, provinsi_kode } }).then(r => r.data),
  getMapDataKecamatan:(tahun, kabkota_kode)  => api.get(`${PUBLIC}/map`, { params: { tahun, kabkota_kode } }).then(r => r.data),

  // ── Dashboard (requires auth) ───────────────────────────────────────────
  getDashParamTahun:  (params) => api.get(`/report/paramtahun`,{ params }).then(r => r.data),
  getDashParamLembaga:(params) => api.get(`/report/paramlaz`,  { params }).then(r => r.data),
  getDashParamProv:   (params) => api.get(`/report/paramprov`, { params }).then(r => r.data),
  getDashParamkab:    (params) => api.get(`/report/paramkab`,  { params }).then(r => r.data),
  getDashParamkec:    (params) => api.get(`/report/paramkec`,  { params }).then(r => r.data),

  getDashBaseWilayah: (params) => api.get(`/report/basewil`,   { params }).then(r => r.data),
  getDashDataWilayah: (params) => api.get(`/report/datawil`,   { params }).then(r => r.data),
  getDashBaseDesil:   (params) => api.get(`/report/basedesil`, { params }).then(r => r.data),
  getDashDataDesil:   (params) => api.get(`/report/datadesil`, { params }).then(r => r.data),
  getDashDataBidang:  (params) => api.get(`/report/databidang`,{ params }).then(r => r.data),
  getDashDataUsia:    (params) => api.get(`/report/datausia`,  { params }).then(r => r.data),
  getDashSummary:     (params) => api.get(`/report/summary`,   { params }).then(r => r.data),
  getDashMustahik:    (params) => api.get(`/report/mustahik`,  { params }).then(r => r.data),
  getDashGender:      (params) => api.get(`/report/gender`,    { params }).then(r => r.data),
  getDashBidang:      (params) => api.get(`/report/bidang`,    { params }).then(r => r.data),
  getDashTimeseries:  (params) => api.get(`/report/timeseries`,{ params }).then(r => r.data),
}
