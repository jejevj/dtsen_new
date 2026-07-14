import api from './api'

export default {
  getList: (params) => api.get('/mustahik', { params }).then((r) => r.data),
  getDetail: (nikHashed) => api.get(`/mustahik/${nikHashed}`).then((r) => r.data)
}
