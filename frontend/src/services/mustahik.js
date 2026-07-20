import api from './api'

export default {
  getList:        (params)     => api.get('/mustahik', { params }).then((r) => r.data),
  getDetail:      (nikHashed)  => api.get(`/mustahik/${nikHashed}`).then((r) => r.data),
  // Endpoint baru — NIK plain, tidak di-hash (lebih cepat karena pakai index)
  getDetailByNik: (nik)        => api.get(`/mustahik/by-nik/${nik}`).then((r) => r.data),
}
