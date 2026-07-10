import api from './api'

// Endpoint publik — digunakan di landing page tanpa token
const PUBLIC = '/public/report'

// Endpoint private — digunakan di dashboard (butuh JWT)
const PRIVATE = '/report'

const ReportService = {
  // ── Landing page (no auth) ──
  getHomeSummary:  ()       => api.get(`${PUBLIC}/summary`).then(r => r.data),
  getByGender:     (_p)     => api.get(`${PUBLIC}/gender`).then(r => r.data),
  getByBidang:     (_p)     => api.get(`${PUBLIC}/bidang`).then(r => r.data),
  getTimeseries:   (_p)     => api.get(`${PUBLIC}/timeseries`).then(r => r.data),
  getMapData:      (level)  => api.get(`${PUBLIC}/map`, { params: { level } }).then(r => r.data),

  // ── Dashboard (requires auth) ──
  getSummary:      (params) => api.get(`${PRIVATE}/summary`,   { params }).then(r => r.data),
  getGender:       (params) => api.get(`${PRIVATE}/gender`,    { params }).then(r => r.data),
  getBidang:       (params) => api.get(`${PRIVATE}/bidang`,    { params }).then(r => r.data),
  getTimeseriesAuth: (p)    => api.get(`${PRIVATE}/timeseries`,{ params: p }).then(r => r.data),
  getDesil:        (params) => api.get(`${PRIVATE}/desil`,     { params }).then(r => r.data),
  getTabulate:     (params) => api.get(`${PRIVATE}/tabulate`,  { params }).then(r => r.data),
}

export default ReportService
