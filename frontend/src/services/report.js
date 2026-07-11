import api from './api'

const PUBLIC = '/public/report'

export default {
  // ── Public (no auth) ────────────────────────────────────────────────────
  getSummary:    ()                             => api.get(`${PUBLIC}/summary`).then(r => r.data),
  getGender:     ()                             => api.get(`${PUBLIC}/gender`).then(r => r.data),
  getBidang:     ()                             => api.get(`${PUBLIC}/bidang`).then(r => r.data),
  getTimeseries: (_p)                           => api.get(`${PUBLIC}/timeseries`).then(r => r.data),

  // level=1 → provinsi | level=2&provinsi_kode=XX → kabkota | level=3&kabkota_kode=XX → kecamatan
  getMapData:          (level)                  => api.get(`${PUBLIC}/map`, { params: { level } }).then(r => r.data),
  getMapDataKabkota:   (provinsi_kode)          => api.get(`${PUBLIC}/map`, { params: { level: '2', provinsi_kode } }).then(r => r.data),
  getMapDataKecamatan: (kabkota_kode)           => api.get(`${PUBLIC}/map`, { params: { level: '3', kabkota_kode } }).then(r => r.data),

  // ── Dashboard (requires auth) ───────────────────────────────────────────
  getDashboardSummary: (params)                 => api.get('/report/summary',   { params }).then(r => r.data),
  getDashboardGender:  (params)                 => api.get('/report/gender',    { params }).then(r => r.data),
  getDashboardBidang:  (params)                 => api.get('/report/bidang',    { params }).then(r => r.data),
  getDashboardTimeseries: (params)              => api.get('/report/timeseries',{ params }).then(r => r.data),
  getDesil:            (params)                 => api.get('/report/desil',     { params }).then(r => r.data),
  getTabulate:         (params)                 => api.get('/report/tabulate',  { params }).then(r => r.data),
}
