import api from './api'
import {
  mockHomeSummary, mockByGender, mockByBidang,
  mockTimeseries, mockMapData, mockSummary, mockDesilSummary
} from './mock'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

const maybe = (mockFn, apiFn) => USE_MOCK ? mockFn() : apiFn()

export default {
  getSummary:    (params) => maybe(mockSummary,      () => api.get('/report/summary',    { params }).then(r => r.data)),
  getByGender:   (params) => maybe(mockByGender,     () => api.get('/report/gender',     { params }).then(r => r.data)),
  getByBidang:   (params) => maybe(mockByBidang,     () => api.get('/report/bidang',     { params }).then(r => r.data)),
  getTimeseries: (params) => maybe(mockTimeseries,   () => api.get('/report/timeseries', { params }).then(r => r.data)),
  getDesilSummary:(params)=> maybe(mockDesilSummary, () => api.get('/report/desil',      { params }).then(r => r.data)),
  getTabulate:   (params) => api.get('/report/tabulate', { params }).then(r => r.data),
  getHomeSummary:()       => maybe(mockHomeSummary,  () => api.get('/home/summary').then(r => r.data)),
  getMapData:    (type)   => maybe(mockMapData,      () => api.get('/home/map', { params: { type } }).then(r => r.data)),
}
