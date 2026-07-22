import api from './api'
import { fetchBaselineAnggotaByNik } from './baselineService'

export default {
  getList:             (params)      => api.get('/mustahik', { params }).then((r) => r.data),
  getDetail:           (nikHashed)   => api.get(`/mustahik/${nikHashed}`).then((r) => r.data),
  // Endpoint mustahik — NIK plain, detail penerima manfaat
  getDetailByNik:      (nik)         => api.get(`/mustahik/by-nik/${nik}`).then((r) => r.data),
  // Endpoint riwayat penerimaan bantuan — semua LAZ (all-LAZ, no filter)
  getRiwayatByNikHashed: (nikHashed) => api.get(`/mustahik/${nikHashed}/riwayat`).then((r) => r.data),
  // Endpoint ZAWA/baseline — cek apakah NIK terdata di DTSEN (loop per-provinsi)
  getZawaAnggotaByNik: (nik)         => fetchBaselineAnggotaByNik(nik),
}
