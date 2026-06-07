import api from './api'

export default {
  getSummary: (params) => api.get('/report/summary', { params }).then((r) => r.data),
  getByGender: (params) => api.get('/report/gender', { params }).then((r) => r.data),
  getByBidang: (params) => api.get('/report/bidang', { params }).then((r) => r.data),
  getTimeseries: (params) => api.get('/report/timeseries', { params }).then((r) => r.data),
  getDesilSummary: (params) => api.get('/report/desil', { params }).then((r) => r.data),
  getTabulate: (params) => api.get('/report/tabulate', { params }).then((r) => r.data),
  getHomeSummary: () => api.get('/home/summary').then((r) => r.data),
  getMapData: (type) => api.get('/home/map', { params: { type } }).then((r) => r.data)
}
