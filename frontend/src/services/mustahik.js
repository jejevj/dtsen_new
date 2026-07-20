import api from './api'
import { fetchBaselineAnggotaByNik } from './baselineService'

export default {
  getList:        (params)     => api.get('/mustahik', { params }).then((r) => r.data),
  getDetail:      (nikHashed)  => api.get(`/mustahik/${nikHashed}`).then((r) => r.data),
  // Endpoint mustahik — NIK plain, riwayat penerimaan zakat/bantuan
  getDetailByNik: (nik)        => api.get(`/mustahik/by-nik/${nik}`).then((r) => r.data),
  // Endpoint ZAWA/baseline — cek apakah NIK terdata di DTSEN
  getZawaAnggotaByNik: (nik)   => fetchBaselineAnggotaByNik(nik),
}
