<template>
  <AppLayout>
    <div style="display:flex;flex-direction:column;gap:20px;">
      <button @click="$router.back()" style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border:1px solid #e2e8f0;border-radius:8px;background:white;font-size:13px;font-weight:600;cursor:pointer;color:#374151;width:fit-content;">
        <i class="pi pi-arrow-left" style="font-size:11px;"></i> Kembali
      </button>
      <div v-if="loading" class="state-card">
        <div class="loader-circle"></div>
        <h3>Memuat Data Penerima Manfaat</h3>
        <p>Sedang mengambil informasi penerima manfaat...</p>

        <div class="loading-bars">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <div v-else-if="error" class="state-card error-state">
        <div class="state-icon error">
          <i class="pi pi-exclamation-triangle"></i>
        </div>

        <h3>Terjadi Kesalahan</h3>
        <p>{{ error }}</p>

        <button class="state-btn" @click="loadDetail">
          <i class="pi pi-refresh"></i>
          Coba Lagi
        </button>
      </div>

      <div v-else-if="!mustahik" class="state-card empty-state">
        <div class="state-icon empty">
          <i class="pi pi-search"></i>
        </div>
        <h3>Data Tidak Ditemukan</h3>
        <p>
          Data Penerima Manfaat yang Anda cari tidak tersedia atau sudah tidak dapat diakses.
        </p>
        <button class="state-btn" @click="$router.back()">
          <i class="pi pi-arrow-left"></i>
          Kembali
        </button>
      </div>

      <template v-else>
        <div class="grid-2">
          <div class="detail-card wm-card">
            <div class="wm-overlay" aria-hidden="true">
              <svg class="wm-svg" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <pattern id="wm-pribadi" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
                    <text x="10" y="40" font-family="Inter, sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text>
                    <text x="10" y="70" font-family="Inter, sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text>
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#wm-pribadi)" />
              </svg>
            </div>
            <div style="position:relative;z-index:1;">
              <p class="section-title"><i class="pi pi-id-card"></i> Data Pribadi</p>
              <table class="info-table">
                <tbody>
                  <tr>
                    <td>
                      <div style="display:flex;align-items:center;gap:20px;">
                        <div :style="{
                            width:'80px',
                            height:'80px',
                            borderRadius:'16px',
                            background:DESIL_COLORS[mustahik.desil].bg,
                            display:'flex',
                            alignItems:'center',
                            justifyContent:'center',
                            flexShrink:0,
                            border:'2px solid '+DESIL_COLORS[mustahik.desil].border
                        }">
                          <i
                            class="pi pi-user"
                            :style="{
                              fontSize:'24px',
                              color:DESIL_COLORS[mustahik.desil].text
                            }"
                          ></i>
                        </div>

                        <div style="flex:1;">
                          <h2 style="margin:0;font-size:1.1rem;font-weight:700;color:#1e293b;">
                            {{ mustahik.nama_lengkap }}
                          </h2>
                        </div>
                      </div>
                    </td>
                  </tr>
                  <tr><td class="td-label">NIK</td><td class="td-value">{{ maskNIK(mustahik.nik) }}</td></tr>
                  <tr><td class="td-label">Jenis Kelamin</td><td class="td-value">{{ mustahik.jenis_kelamin==='m'?'Laki-laki':'Perempuan' }}</td></tr>
                  <tr><td class="td-label">Usia</td><td class="td-value">{{ mustahik.usia }} tahun</td></tr>
                  <tr><td class="td-label">Agama</td><td class="td-value">{{ mustahik.agama }}</td></tr>
                  <tr><td class="td-label">Jumlah Tanggungan</td><td class="td-value">{{ mustahik.tanggungan }} jiwa</td></tr>
                  <tr><td class="td-label">Usia</td><td class="td-value">{{ mustahik.usia }} Tahun</td></tr>
                  <tr><td class="td-label">Status Pernikahan</td><td class="td-value">{{ mustahik.status_pernikahan }}</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Alamat -->
          <div class="detail-card wm-card">
            <div class="wm-overlay" aria-hidden="true">
              <svg class="wm-svg" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <pattern id="wm-alamat" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
                    <text x="10" y="40" font-family="Inter, sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text>
                    <text x="10" y="70" font-family="Inter, sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text>
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#wm-alamat)" />
              </svg>
            </div>
            <div style="position:relative;z-index:1;">
              <p class="section-title"><i class="pi pi-map-marker"></i> Alamat Domisili</p>
              <table class="info-table">
                <tbody>
                  <tr><td class="td-label">Alamat</td><td class="td-value">{{ mustahik.alamat_domisili }}</td></tr>
                  <tr><td class="td-label">Kelurahan</td><td class="td-value">{{ mustahik.kelurahan_nama }}</td></tr>
                  <tr><td class="td-label">Kecamatan</td><td class="td-value">{{ mustahik.kecamatan_nama }}</td></tr>
                  <tr><td class="td-label">Kab / Kota</td><td class="td-value">{{ mustahik.kabkota_nama  }}</td></tr>
                  <tr><td class="td-label">Provinsi</td><td class="td-value">{{ mustahik.provinsi_nama }}</td></tr>
                  
                </tbody>
              </table>
              <p class="section-title"><i class="pi pi-map-marker"></i> Alamat KTP</p>
              <table class="info-table">
                <tbody>
                  <tr><td class="td-label">Alamat</td><td class="td-value">{{ mustahik.ktp_alamat }}</td></tr>
                  <tr><td class="td-label">Kelurahan</td><td class="td-value">{{ mustahik.ktp_kelurahan_nama }}</td></tr>
                  <tr><td class="td-label">Kecamatan</td><td class="td-value">{{ mustahik.ktp_kecamatan_nama }}</td></tr>
                  <tr><td class="td-label">Kab / Kota</td><td class="td-value">{{ mustahik.ktp_kabkota_nama  }}</td></tr>
                  <tr><td class="td-label">Provinsi</td><td class="td-value">{{ mustahik.ktp_provinsi_nama }}</td></tr>
                  
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div
          style="display:flex;justify-content:flex-start;align-items:center;gap:10px;margin-bottom:14px"
        >
          <span
            style="font-size:13px;font-weight:600;color:#64748b"
          >
            Lembaga Penyalur Bantuan :
          </span>
          <Select
            v-model="filterLaz"
            :options="lazOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Semua Lembaga"
            style="width:280px"
            :disabled="!!authStore.user?.laz_kode"
          />
        </div>
        <div class="detail-card wm-card">
          <div class="wm-overlay" aria-hidden="true">
            <svg class="wm-svg" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <pattern id="wm-riwayat" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
                  <text x="10" y="40" font-family="Inter, sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text>
                  <text x="10" y="70" font-family="Inter, sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text>
                </pattern>
              </defs>
            </svg>
          </div>
          <p class="section-title"><i class="pi pi-wallet"></i> Ringkasan Penerimaan Bantuan</p>
          <div class="grid-3">
            <div class="stat-box" style="background:#f0fdf4;">
                <p class="stat-label">Bantuan Tahun Ini</p>
                <template v-if="loadingRiwayat">
                    <p class="stat-loading">Memuat...</p>
                </template>
                <template v-else>
                    <p class="stat-val" style="color:#15803d;">
                        {{ formatRupiah(bantuanTahunIni) }}
                    </p>
                </template>
            </div>

            <div class="stat-box" style="background:#fdf4ff;">
                <p class="stat-label">Total Kumulatif</p>

                <template v-if="loadingRiwayat">
                    <p class="stat-loading">Memuat...</p>
                </template>
                <template v-else>
                    <p class="stat-val" style="color:#7c3aed;">
                        {{ formatRupiah(totalKumulatif) }}
                    </p>
                </template>
            </div>

            <div class="stat-box" style="background:#eff6ff;">
                <p class="stat-label">Total LAZ Berkontribusi</p>

                <template v-if="loadingRiwayat">
                    <p class="stat-loading">Memuat...</p>
                </template>
                <template v-else>
                    <p class="stat-val" style="color:#2563eb;">
                        {{ totalLazKontributor }}
                    </p>
                </template>

                <p style="font-size:11px;color:#64748b;margin-top:4px;">
                    LAZ berbeda yang pernah menyalurkan bantuan
                </p>
            </div>
          </div>
        </div>
        <div class="detail-card wm-card">
          <div class="wm-overlay" aria-hidden="true">
            <svg class="wm-svg" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <pattern id="wm-rekap" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
                  <text x="10" y="40" font-family="Inter, sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text>
                  <text x="10" y="70" font-family="Inter, sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#wm-rekap)" />
            </svg>
          </div>
          <div style="position:relative;z-index:1;">
            <p class="section-title"><i class="pi pi-history"></i> Ringkasan Penerimaan Bantuan / Tahun</p>
            <div style="overflow-x:auto">
                  <table class="data-table">
                      <thead>
                          <tr>
                              <th>Tahun</th>
                              <th>Total Penerimaan</th>
                              <th>Penerimaan Langsung</th>
                              <th>Penerimaan Tidak Langsung</th>
                          </tr>
                      </thead>
                      <tbody>
                          <tr v-if="loadingRiwayat">
                              <td colspan="4" class="table-info">
                                  Memuat data...
                              </td>
                          </tr>
                          <tr
                              v-else
                              v-for="row in rekapPenyaluran"
                              :key="row.tahun"
                          >
                              <td>
                                  <strong>{{ row.tahun }}</strong>
                              </td>
                              <td>
                                  <span
                                      style="background:#eff6ff;color:#2563eb;padding:4px 10px;border-radius:999px;font-weight:700;"
                                  >
                                      {{ formatRupiah(row.total) }}
                                  </span>
                              </td>
                              <td>
                                  {{ formatRupiah(row.langsung) }}
                              </td>
                              <td>
                                  {{ formatRupiah(row.tidakLangsung) }}
                              </td>
                          </tr>
                          <tr
                              v-if="!loadingRiwayat && rekapPenyaluran.length===0"
                          >
                              <td colspan="4" class="table-info">
                                  Belum ada data.
                              </td>
                          </tr>
                      </tbody>
                  </table>
              </div>
            
          </div>
        </div>
        <div class="detail-card wm-card">
          <div class="wm-overlay" aria-hidden="true">
            <svg class="wm-svg" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <pattern id="wm-detail-riwayat" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
                  <text x="10" y="40" font-family="Inter, sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text>
                  <text x="10" y="70" font-family="Inter, sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#wm-detail-riwayat)" />
            </svg>
          </div>
          
          <div style="position:relative;z-index:1;">
            <p class="section-title"><i class="pi pi-history"></i> Riwayat Penerimaan Bantuan</p>
            <div style="overflow-x:auto;">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Tahun</th>
                    <th>Laz</th>
                    <th>Periode</th>
                    <th>Program</th>
                    <th>Bidang</th>
                    <th>Nominal</th>
                    <th>Tipe Penerimaan</th>
                    <th>Tanggal Cair</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="loadingRiwayat">
                      <td colspan="8" class="table-info">
                          <i class="pi pi-spin pi-spinner"></i>
                          Memuat riwayat penyaluran bantuan...
                      </td>
                  </tr>
                  <tr v-else-if="riwayatFiltered.length === 0">
                      <td colspan="8" class="table-info">
                          Belum ada riwayat penyaluran bantuan.
                      </td>
                  </tr>
                  <tr
                      v-else
                      v-for="(item,i) in riwayatFiltered"
                      :key="i"
                  >
                      <td>{{ item.tahun }}</td>
                      <td>{{ item.laz }}</td>
                      <td>{{ item.periode }}</td>
                      <td>{{ item.program }}</td>
                      <td>{{ item.bidang }}</td>
                      <td>
                          <span style="padding:2px 10px;border-radius:99px;font-size:11px;font-weight:700;background:#dcfce7;color:#15803d;">
                              {{ formatRupiah(item.nominal) }}
                          </span>
                      </td>
                      <td>{{ item.metode }}</td>
                      <td>{{ item.tanggal }}</td>
                  </tr>
              </tbody>
              </table>
            </div>
          </div>
        </div>
      </template>
    </div>
  </AppLayout>
</template>

<script setup>
import { useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { formatRupiah } from '@/utils/formatter'
import { useAuthStore } from '@/stores/auth'
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import Select from 'primevue/select'
import { useWatermark } from '@/composables/useWatermark'

const authStore = useAuthStore()
const { userIdentifier } = useWatermark()

const filterLaz = ref(authStore.user?.laz_kode || '')
const route = useRoute()
const mustahik = ref(null)
const loading = ref(true)
const error = ref('')
const riwayat = ref([])
const programSosial = ref([])
const loadingRiwayat = ref(true)

async function loadRiwayat() {
    loadingRiwayat.value = true

    try {
        const res = await api.get(`/mustahik/${route.params.nikHashed}/riwayat`)
        riwayat.value = res.data.data ?? []
        filterLaz.value = authStore.user?.laz_kode || ''
    } finally {
        loadingRiwayat.value = false
    }
}
async function loadDetail() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get(`/mustahik/${route.params.nikHashed}`)
    mustahik.value = res.data.data?.[0] ?? null
  } catch (err) {
    error.value = err?.response?.data?.message ?? 'Data tidak ditemukan'
  } finally {
    loading.value = false
  }
}

const lazOptions = computed(() => {
    const map = new Map()

    riwayat.value.forEach(item => {
        if (item.laz_kode && !map.has(item.laz_kode)) {
            map.set(item.laz_kode, {
                label: item.laz,
                value: item.laz_kode
            })
        }
    })

    return [
        { label: 'Semua Lembaga', value: '' },
        ...map.values()
    ]
})



onMounted(() => {
    loadDetail()
    loadRiwayat()
})

const riwayatFiltered = computed(() => {
    console.log('filterLaz', filterLaz.value)

    console.log(riwayat.value)

    return riwayat.value.filter(item => {
        console.log(
            item.laz,
            item.laz_kode
        )

        return item.laz_kode === filterLaz.value
    })
})

const bantuanTahunIni = computed(() => {
    const tahunSekarang = new Date().getFullYear()

    return riwayatFiltered.value
        .filter(item => Number(item.tahun) === tahunSekarang)
        .reduce((t, item) => t + Number(item.nominal || 0), 0)
})

const totalKumulatif = computed(() => {
    return riwayatFiltered.value.reduce((t, r) => {
        return t + Number(r.nominal || 0)
    }, 0)
})

const totalLazKontributor = computed(() => {
    return new Set(
        riwayatFiltered.value
            .map(item => item.laz?.trim().toLowerCase())
            .filter(Boolean)
    ).size
})

const rekapPenyaluran = computed(() => {
    const result = {}
    riwayatFiltered.value.forEach(item => {
        const tahun = item.tahun
        const nominal = Number(item.nominal || 0)
        if (!result[tahun]) {
            result[tahun] = {
                tahun,
                total: 0,
                langsung: 0,
                tidakLangsung: 0
            }
        }
        result[tahun].total += nominal
        const metode = (item.metode || "").toLowerCase()
        if (item.metode === "Penerima Manfaat Langsung") {
            result[tahun].langsung += nominal
        }
        if (item.metode === "Penerima Manfaat Tidak Langsung") {
            result[tahun].tidakLangsung += nominal
        }
    })

    return Object.values(result).sort((a, b) => b.tahun - a.tahun)
})

const DESIL_COLORS = {
  1: {
    bg: '#fee2e2',
    text: '#b91c1c',
    border: '#fecaca'
  },
  2: {
    bg: '#fef3c7',
    text: '#b45309',
    border: '#fde68a'
  },
  3: {
    bg: '#dcfce7',
    text: '#15803d',
    border: '#bbf7d0'
  },
  4: {
    bg: '#dbeafe',
    text: '#2563eb',
    border: '#bfdbfe'
  }
}

function maskNIK(nik) {
  if (!nik) return '-'
  return nik.slice(0, 6) + '*********' + nik.slice(-1)
}

function desilLabel(d) {
  return { 1: 'Sangat Miskin', 2: 'Miskin', 3: 'Hampir Miskin', 4: 'Rentan Miskin' }[d] || '-'
}

function keteranganBadges(ket) {
  if (!ket || ket === '-') return []
  return ket.split(/[,&]/).map(s => s.trim()).filter(Boolean)
}

function fakeKodePos(id) {
  const base = [16110, 15111, 50171, 60172, 40111]
  return String(base[(id - 1) % base.length] + id)
}



</script>

<style scoped>
/* ===== LAYOUT ===== */
.grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.grid-3 { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
@media(max-width:768px) {
  .grid-2 { grid-template-columns:1fr; }
  .grid-3 { grid-template-columns:1fr; }
}

/* ===== CARD ===== */
.detail-card {
  background:white;
  border-radius:14px;
  border:1px solid #f1f5f9;
  padding:22px;
  box-shadow:0 1px 4px rgba(0,0,0,0.04);
}

/* Card dengan watermark — butuh position:relative & overflow:hidden */
.wm-card {
  position: relative;
  overflow: hidden;
}

/* Overlay watermark: isi penuh card */
.wm-overlay {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  user-select: none;
  -webkit-user-select: none;
}

/* SVG memenuhi 100% lebar & tinggi card */
.wm-svg {
  display: block;
  width: 100%;
  height: 100%;
}

.section-title {
  font-size:13px;
  font-weight:700;
  color:#374151;
  margin:0 0 14px;
  display:flex;
  align-items:center;
  gap:6px;
}

/* ===== BADGE ===== */
.badge {
  padding:3px 10px;
  border-radius:99px;
  font-size:11px;
  font-weight:700;
}

/* ===== INFO TABLE (label-value) ===== */
.info-table { width:100%; border-collapse:collapse; }
.info-table tr { border-bottom:1px solid #f8fafc; }
.info-table tr:last-child { border-bottom:none; }
.td-label {
  font-size:12px;
  color:#94a3b8;
  font-weight:500;
  padding:9px 4px;
  width:35%;
  vertical-align:top;
}
.td-value {
  font-size:13px;
  color:#374151;
  font-weight:600;
  padding:9px 4px;
  text-align:right;
}
.th {
  font-size:11px;
  color:#94a3b8;
  font-weight:600;
  text-transform:uppercase;
  letter-spacing:.5px;
  padding:6px 8px;
  text-align:left;
  border-bottom:1px solid #f1f5f9;
}

/* ===== DATA TABLE (anggota / riwayat) ===== */
.data-table {
  width:100%;
  border-collapse:collapse;
  font-size:13px;
  min-width:560px;
}
.data-table thead tr { background:#f8fafc; }
.data-table th {
  font-size:11px;
  color:#94a3b8;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:.5px;
  padding:10px 12px;
  text-align:left;
  border-bottom:1px solid #f1f5f9;
  white-space:nowrap;
}
.data-table td {
  padding:10px 12px;
  border-bottom:1px solid #f8fafc;
  vertical-align:middle;
}
.data-table tbody tr:last-child td { border-bottom:none; }
.data-table tbody tr:hover { background:rgba(240,249,255,0.85); }

/* ===== STAT BOX ===== */
.stat-box { border-radius:10px; padding:16px; }
.stat-label {
  font-size:11px;
  color:#64748b;
  font-weight:600;
  text-transform:uppercase;
  letter-spacing:.5px;
  margin:0 0 4px;
}
.stat-val { font-size:1.25rem; font-weight:900; margin:0; }

        /* ===========================
        LOADING / EMPTY / ERROR
      =========================== */

      .state-card{
          background:#fff;
          border:1px solid #eef2f7;
          border-radius:18px;
          padding:70px 30px;
          text-align:center;
          box-shadow:0 10px 30px rgba(15,23,42,.05);
      }

      .state-card h3{
          margin:22px 0 8px;
          font-size:22px;
          font-weight:800;
          color:#1e293b;
      }

      .state-card p{
          margin:0;
          color:#64748b;
          font-size:14px;
          line-height:1.7;
      }

      /* ===========================
        Spinner
      =========================== */

      .loader-circle{
          width:72px;
          height:72px;
          margin:auto;
          border-radius:50%;
          border:6px solid #e2e8f0;
          border-top:6px solid #2563eb;
          animation:spin .9s linear infinite;
      }

      @keyframes spin{
          to{
              transform:rotate(360deg);
          }
      }

      /* ===========================
        Loading dots
      =========================== */

      .loading-bars{
          margin-top:28px;
          display:flex;
          justify-content:center;
          gap:8px;
      }

      .loading-bars span{
          width:10px;
          height:10px;
          border-radius:50%;
          background:#3b82f6;
          animation:bounce 1.2s infinite ease-in-out;
      }

      .loading-bars span:nth-child(2){
          animation-delay:.2s;
      }

      .loading-bars span:nth-child(3){
          animation-delay:.4s;
      }

      @keyframes bounce{
          0%,80%,100%{
              transform:scale(.5);
              opacity:.4;
          }
          40%{
              transform:scale(1.2);
              opacity:1;
          }
      }

      /* ===========================
        Icons
      =========================== */

      .state-icon{
          width:90px;
          height:90px;
          margin:auto;
          border-radius:50%;
          display:flex;
          align-items:center;
          justify-content:center;
          font-size:38px;
      }

      .state-icon.error{
          background:#fef2f2;
          color:#dc2626;
      }

      .state-icon.empty{
          background:#eff6ff;
          color:#2563eb;
      }

      /* ===========================
        Button
      =========================== */

      .state-btn{
          margin-top:28px;
          border:none;
          border-radius:10px;
          padding:11px 22px;
          background:#2563eb;
          color:white;
          font-weight:700;
          cursor:pointer;
          display:inline-flex;
          align-items:center;
          gap:8px;
          transition:.25s;
      }

      .state-btn:hover{
          background:#1d4ed8;
          transform:translateY(-2px);
          box-shadow:0 10px 20px rgba(37,99,235,.25);
      }

      .stat-loading{
          margin:0;
          font-size:15px;
          font-weight:700;
          color:#64748b;
      }

      .table-info{
          text-align:center;
          padding:35px !important;
          color:#64748b;
          font-weight:600;
      }

      .table-info i{
          margin-right:8px;
      }
      </style>
