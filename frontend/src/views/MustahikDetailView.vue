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
                <pattern id="wm-riwayat" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
                  <text x="10" y="40" font-family="Inter, sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text>
                  <text x="10" y="70" font-family="Inter, sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#wm-riwayat)" />
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
                <pattern id="wm-riwayat" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
                  <text x="10" y="40" font-family="Inter, sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text>
                  <text x="10" y="70" font-family="Inter, sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#wm-riwayat)" />
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

const authStore = useAuthStore()
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

const userIdentifier = computed(() => {
  const u = authStore.user
  if (!u) return 'CONFIDENTIAL'
  return u.email || u.tuser_email || u.notelp || u.user_id || 'CONFIDENTIAL'
})

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
      <!-- Back -->
<template>
  <AppLayout>
    <div style="display:flex;flex-direction:column;gap:20px;">

      <!-- Back -->
      <button @click="$router.back()" style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border:1px solid #e2e8f0;border-radius:8px;background:white;font-size:13px;font-weight:600;cursor:pointer;color:#374151;width:fit-content;">
        <i class="pi pi-arrow-left" style="font-size:11px;"></i> Kembali
      </button>

      <!-- Not found -->
      <div v-if="!mustahik" style="text-align:center;padding:60px 20px;background:white;border-radius:14px;border:1px solid #f1f5f9;">
        <i class="pi pi-user-minus" style="font-size:40px;color:#cbd5e1;"></i>
        <p style="color:#64748b;margin:12px 0 0;">Data tidak ditemukan</p>
      </div>

      <template v-else>

        <!-- ===== HEADER IDENTITY ===== -->
        <div style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:28px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
          <div style="display:flex;align-items:flex-start;gap:20px;flex-wrap:wrap;">
            <!-- Avatar -->
            <div :style="{ width:'80px', height:'80px', borderRadius:'16px', background:DESIL_COLORS[mustahik.desil].bg, display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0, border:'2px solid '+DESIL_COLORS[mustahik.desil].border }">
              <i class="pi pi-user" :style="{ fontSize:'32px', color:DESIL_COLORS[mustahik.desil].text }"></i>
            </div>

            <div style="flex:1;min-width:0;">
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px;">
                <h2 style="font-size:1.25rem;font-weight:800;color:#1e293b;margin:0;">{{ mustahik.nama }}</h2>
                <span class="badge" :style="{ background:DESIL_COLORS[mustahik.desil].bg, color:DESIL_COLORS[mustahik.desil].text }">Desil {{ mustahik.desil }} — {{ desilLabel(mustahik.desil) }}</span>
                <span class="badge" :style="{ background: mustahik.jenis_kelamin==='m'?'#eff6ff':'#fdf2f8', color: mustahik.jenis_kelamin==='m'?'#2563eb':'#db2777' }">{{ mustahik.jenis_kelamin==='m'?'Laki-laki':'Perempuan' }}</span>
              </div>
              <p style="font-size:13px;color:#64748b;margin:0 0 6px;">NIK: <strong style="color:#374151;font-family:monospace;">{{ maskNIK(mustahik.nik) }}</strong></p>
              <div v-if="keteranganBadges(mustahik.keterangan).length" style="display:flex;gap:6px;flex-wrap:wrap;">
                <span v-for="k in keteranganBadges(mustahik.keterangan)" :key="k" style="display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:99px;font-size:11px;font-weight:600;background:#fef3c7;color:#b45309;">
                  <i class="pi pi-flag" style="font-size:10px;"></i> {{ k }}
                </span>
              </div>
            </div>

            <div style="text-align:right;flex-shrink:0;">
              <p style="font-size:11px;color:#94a3b8;margin:0;font-weight:600;text-transform:uppercase;letter-spacing:.5px;">Total Bantuan</p>
              <p style="font-size:1.5rem;font-weight:900;color:#15803d;margin:2px 0 0;">{{ formatRupiah(mustahik.nominal) }}</p>
              <span style="font-size:11px;color:#22c55e;font-weight:600;">&#x2714; Aktif 2024</span>
            </div>
          </div>
        </div>

        <!-- ===== GRID ROW 1: Data Pribadi + Alamat ===== -->
        <div class="grid-2">

          <!-- Data Pribadi -->
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
                  <tr><td class="td-label">Usia</td><td class="td-value">{{ mustahik.usia }} tahun</td></tr>
                  <tr><td class="td-label">Agama</td><td class="td-value">{{ mustahik.agama }}</td></tr>
                  <tr><td class="td-label">Status Pernikahan</td><td class="td-value">{{ mustahik.status_pernikahan }}</td></tr>
                  <tr><td class="td-label">Pekerjaan</td><td class="td-value">{{ mustahik.pekerjaan }}</td></tr>
                  <tr>
                    <td class="td-label">Penghasilan/Bln</td>
                    <td class="td-value" :style="{ color: mustahik.penghasilan===0 ? '#dc2626':'#374151' }">
                      {{ mustahik.penghasilan===0 ? 'Tidak ada penghasilan' : formatRupiah(mustahik.penghasilan) }}
                    </td>
                  </tr>
                  <tr><td class="td-label">Jumlah Tanggungan</td><td class="td-value">{{ mustahik.jumlah_tanggungan }} jiwa</td></tr>
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
                  <tr><td class="td-label">Kelurahan</td><td class="td-value">{{ mustahik.kelurahan }}</td></tr>
                  <tr><td class="td-label">Kecamatan</td><td class="td-value">{{ mustahik.kecamatan }}</td></tr>
                  <tr><td class="td-label">Kab / Kota</td><td class="td-value">{{ mustahik.kab_kota }}</td></tr>
                  <tr><td class="td-label">Provinsi</td><td class="td-value">{{ mustahik.provinsi }}</td></tr>
                  <tr><td class="td-label">Kode Pos</td><td class="td-value">{{ fakeKodePos(mustahik.id) }}</td></tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>

        <!-- ===== PROGRAM SOSIAL (full width) ===== -->
        <div class="detail-card wm-card">
          <div class="wm-overlay" aria-hidden="true">
            <svg class="wm-svg" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <pattern id="wm-program" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
                  <text x="10" y="40" font-family="Inter, sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text>
                  <text x="10" y="70" font-family="Inter, sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#wm-program)" />
            </svg>
          </div>
          <div style="position:relative;z-index:1;">
            <p class="section-title"><i class="pi pi-shield"></i> Program Bantuan Sosial Lain</p>
            <table class="info-table">
              <thead>
                <tr>
                  <th class="th">Program</th>
                  <th class="th">Status</th>
                  <th class="th">Tahun</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="prog in programSosial(mustahik)" :key="prog.nama">
                  <td class="td-label" style="font-weight:600;color:#374151;">{{ prog.nama }}</td>
                  <td class="td-value">
                    <span :style="{ padding:'2px 8px', borderRadius:'99px', fontSize:'11px', fontWeight:'700', background: prog.aktif?'#dcfce7':'#f1f5f9', color: prog.aktif?'#15803d':'#94a3b8' }">
                      {{ prog.aktif ? 'Aktif' : 'Tidak' }}
                    </span>
                  </td>
                  <td class="td-value" style="color:#64748b;">{{ prog.tahun }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ===== ANGGOTA KELUARGA ===== -->
        <div class="detail-card wm-card">
          <div class="wm-overlay" aria-hidden="true">
            <svg class="wm-svg" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <pattern id="wm-keluarga" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
                  <text x="10" y="40" font-family="Inter, sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text>
                  <text x="10" y="70" font-family="Inter, sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#wm-keluarga)" />
            </svg>
          </div>
          <div style="position:relative;z-index:1;">
            <p class="section-title"><i class="pi pi-users"></i> Anggota Keluarga</p>
            <div style="overflow-x:auto;">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>No</th>
                    <th>Nama</th>
                    <th>Hubungan</th>
                    <th>L/P</th>
                    <th>Usia</th>
                    <th>Pekerjaan</th>
                    <th>Pendidikan</th>
                    <th>Ket.</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(anggota, i) in anggotaKeluarga(mustahik)" :key="i">
                    <td style="text-align:center;color:#94a3b8;">{{ i+1 }}</td>
                    <td style="font-weight:600;color:#1e293b;">{{ anggota.nama }}</td>
                    <td><span style="padding:2px 8px;border-radius:99px;font-size:11px;font-weight:600;background:#eff6ff;color:#2563eb;">{{ anggota.hubungan }}</span></td>
                    <td style="text-align:center;"><span :style="{color: anggota.jk==='L'?'#2563eb':'#db2777', fontWeight:'700'}">{{ anggota.jk }}</span></td>
                    <td style="text-align:center;">{{ anggota.usia }} th</td>
                    <td style="color:#64748b;">{{ anggota.pekerjaan }}</td>
                    <td style="color:#64748b;">{{ anggota.pendidikan }}</td>
                    <td>
                      <span v-if="anggota.ket" style="padding:2px 8px;border-radius:99px;font-size:11px;font-weight:600;background:#fef3c7;color:#b45309;">{{ anggota.ket }}</span>
                      <span v-else style="color:#cbd5e1;">—</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ===== RIWAYAT BANTUAN ===== -->
        <div class="detail-card wm-card">
          <div class="wm-overlay" aria-hidden="true">
            <svg class="wm-svg" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <pattern id="wm-riwayat" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
                  <text x="10" y="40" font-family="Inter, sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text>
                  <text x="10" y="70" font-family="Inter, sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#wm-riwayat)" />
            </svg>
          </div>
          <div style="position:relative;z-index:1;">
            <p class="section-title"><i class="pi pi-history"></i> Riwayat Penyaluran Bantuan</p>
            <div style="overflow-x:auto;">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Tahun</th>
                    <th>Periode</th>
                    <th>Program</th>
                    <th>Nominal</th>
                    <th>Metode</th>
                    <th>Status</th>
                    <th>Tanggal Cair</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(riwayat, i) in riwayatBantuan(mustahik)" :key="i">
                    <td style="font-weight:700;color:#374151;">{{ riwayat.tahun }}</td>
                    <td style="color:#64748b;">{{ riwayat.periode }}</td>
                    <td style="font-weight:600;color:#374151;">{{ riwayat.program }}</td>
                    <td style="font-weight:700;color:#15803d;">{{ formatRupiah(riwayat.nominal) }}</td>
                    <td style="color:#64748b;">{{ riwayat.metode }}</td>
                    <td>
                      <span :style="{
                        padding:'2px 10px', borderRadius:'99px', fontSize:'11px', fontWeight:'700',
                        background: riwayat.status==='Tersalurkan'?'#dcfce7':riwayat.status==='Proses'?'#fef3c7':'#fef2f2',
                        color: riwayat.status==='Tersalurkan'?'#15803d':riwayat.status==='Proses'?'#b45309':'#dc2626'
                      }">{{ riwayat.status }}</span>
                    </td>
                    <td style="color:#64748b;font-size:12px;">{{ riwayat.tanggal }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- Subtotal -->
            <div style="display:flex;justify-content:flex-end;margin-top:12px;padding-top:12px;border-top:1px solid #f1f5f9;">
              <div style="text-align:right;">
                <p style="font-size:12px;color:#94a3b8;margin:0;">Total Kumulatif Diterima</p>
                <p style="font-size:1.2rem;font-weight:900;color:#15803d;margin:2px 0 0;">{{ formatRupiah(totalKumulatif(mustahik)) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- ===== INFO PENYALURAN SUMMARY ===== -->
        <div class="detail-card">
          <p class="section-title"><i class="pi pi-wallet"></i> Ringkasan Penyaluran</p>
          <div class="grid-3">
            <div class="stat-box" style="background:#f0fdf4;">
              <p class="stat-label">Bantuan Tahun Ini</p>
              <p class="stat-val" style="color:#15803d;">{{ formatRupiah(mustahik.nominal) }}</p>
            </div>
            <div class="stat-box" style="background:#eff6ff;">
              <p class="stat-label">Desil Kemiskinan</p>
              <p class="stat-val" :style="{color:DESIL_COLORS[mustahik.desil].text}">Desil {{ mustahik.desil }}</p>
              <p style="font-size:11px;color:#64748b;margin:4px 0 0;">{{ desilLabel(mustahik.desil) }}</p>
            </div>
            <div class="stat-box" style="background:#fdf4ff;">
              <p class="stat-label">Total Kumulatif</p>
              <p class="stat-val" style="color:#7c3aed;">{{ formatRupiah(totalKumulatif(mustahik)) }}</p>
              <p style="font-size:11px;color:#64748b;margin:4px 0 0;">Sejak 2022</p>
            </div>
          </div>
        </div>

      </template>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { MOCK_MUSTAHIK, DESIL_COLORS } from '@/data/mockMustahik'
import { formatRupiah } from '@/utils/formatter'
import { useAuthStore } from '@/stores/auth'

const route     = useRoute()
const authStore = useAuthStore()

const mustahik = computed(() => MOCK_MUSTAHIK.find(m => m.nik_hashed === route.params.nikHashed))

const userIdentifier = computed(() => {
  const u = authStore.user
  if (!u) return 'CONFIDENTIAL'
  return u.email || u.tuser_email || u.notelp || u.user_id || 'CONFIDENTIAL'
})

function maskNIK(nik) {
  if (!nik) return '-'
  return nik.slice(0, 6) + '••••' + nik.slice(-4)
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

function programSosial(m) {
  return [
    { nama: 'PKH (Program Keluarga Harapan)', aktif: m.desil <= 2, tahun: '2024' },
    { nama: 'BPJS Kesehatan PBI',             aktif: m.desil <= 3, tahun: '2024' },
    { nama: 'Bantuan Pangan Non Tunai (BPNT)',aktif: m.desil <= 2, tahun: '2024' },
    { nama: 'BLT Dana Desa',                   aktif: m.desil === 1, tahun: '2023' },
    { nama: 'KIP (Kartu Indonesia Pintar)',    aktif: m.jumlah_tanggungan >= 3, tahun: '2024' },
    { nama: 'PIP (Program Indonesia Pintar)',  aktif: m.jumlah_tanggungan >= 4, tahun: '2023' },
  ]
}

function anggotaKeluarga(m) {
  const pools = [
    [
      { nama: m.nama, hubungan: 'Kepala Keluarga', jk: m.jenis_kelamin === 'm' ? 'L' : 'P', usia: m.usia, pekerjaan: m.pekerjaan, pendidikan: 'SD', ket: null },
    ],
    [
      { nama: m.nama, hubungan: 'Kepala Keluarga', jk: m.jenis_kelamin === 'm' ? 'L' : 'P', usia: m.usia, pekerjaan: m.pekerjaan, pendidikan: 'SD', ket: null },
      { nama: namaAnggota(m.id, 1), hubungan: 'Pasangan', jk: m.jenis_kelamin === 'm' ? 'P' : 'L', usia: m.usia - 3, pekerjaan: 'Ibu Rumah Tangga', pendidikan: 'SMP', ket: null },
    ],
    [
      { nama: m.nama, hubungan: 'Kepala Keluarga', jk: m.jenis_kelamin === 'm' ? 'L' : 'P', usia: m.usia, pekerjaan: m.pekerjaan, pendidikan: 'SD', ket: null },
      { nama: namaAnggota(m.id, 1), hubungan: 'Pasangan', jk: m.jenis_kelamin === 'm' ? 'P' : 'L', usia: m.usia - 3, pekerjaan: 'Ibu Rumah Tangga', pendidikan: 'SMP', ket: null },
      { nama: namaAnggota(m.id, 2), hubungan: 'Anak', jk: 'L', usia: 12, pekerjaan: 'Pelajar', pendidikan: 'SD', ket: 'KIP' },
    ],
    [
      { nama: m.nama, hubungan: 'Kepala Keluarga', jk: m.jenis_kelamin === 'm' ? 'L' : 'P', usia: m.usia, pekerjaan: m.pekerjaan, pendidikan: 'SD', ket: null },
      { nama: namaAnggota(m.id, 1), hubungan: 'Pasangan', jk: m.jenis_kelamin === 'm' ? 'P' : 'L', usia: m.usia - 3, pekerjaan: 'Ibu Rumah Tangga', pendidikan: 'SMP', ket: null },
      { nama: namaAnggota(m.id, 2), hubungan: 'Anak', jk: 'L', usia: 14, pekerjaan: 'Pelajar', pendidikan: 'SMP', ket: 'KIP' },
      { nama: namaAnggota(m.id, 3), hubungan: 'Anak', jk: 'P', usia: 8,  pekerjaan: 'Pelajar', pendidikan: 'SD',  ket: null },
    ],
    [
      { nama: m.nama, hubungan: 'Kepala Keluarga', jk: m.jenis_kelamin === 'm' ? 'L' : 'P', usia: m.usia, pekerjaan: m.pekerjaan, pendidikan: 'SD', ket: null },
      { nama: namaAnggota(m.id, 1), hubungan: 'Pasangan', jk: m.jenis_kelamin === 'm' ? 'P' : 'L', usia: m.usia - 2, pekerjaan: 'Ibu Rumah Tangga', pendidikan: 'SD', ket: null },
      { nama: namaAnggota(m.id, 2), hubungan: 'Anak', jk: 'L', usia: 17, pekerjaan: 'Pelajar', pendidikan: 'SMA', ket: 'KIP' },
      { nama: namaAnggota(m.id, 3), hubungan: 'Anak', jk: 'P', usia: 10, pekerjaan: 'Pelajar', pendidikan: 'SD',  ket: null },
      { nama: namaAnggota(m.id, 4), hubungan: 'Orang Tua', jk: 'P', usia: m.usia + 20, pekerjaan: 'Tidak Bekerja', pendidikan: 'SD', ket: 'Lansia' },
    ],
    [
      { nama: m.nama, hubungan: 'Kepala Keluarga', jk: m.jenis_kelamin === 'm' ? 'L' : 'P', usia: m.usia, pekerjaan: m.pekerjaan, pendidikan: 'SD', ket: null },
      { nama: namaAnggota(m.id, 1), hubungan: 'Pasangan', jk: m.jenis_kelamin === 'm' ? 'P' : 'L', usia: m.usia - 2, pekerjaan: 'Ibu Rumah Tangga', pendidikan: 'SD', ket: null },
      { nama: namaAnggota(m.id, 2), hubungan: 'Anak', jk: 'L', usia: 19, pekerjaan: 'Tidak Bekerja', pendidikan: 'SMA', ket: null },
      { nama: namaAnggota(m.id, 3), hubungan: 'Anak', jk: 'P', usia: 14, pekerjaan: 'Pelajar', pendidikan: 'SMP', ket: 'KIP' },
      { nama: namaAnggota(m.id, 4), hubungan: 'Anak', jk: 'L', usia: 9,  pekerjaan: 'Pelajar', pendidikan: 'SD',  ket: null },
      { nama: namaAnggota(m.id, 5), hubungan: 'Orang Tua', jk: 'L', usia: m.usia + 22, pekerjaan: 'Tidak Bekerja', pendidikan: 'SD', ket: 'Lansia' },
    ],
  ]
  const idx = Math.min(m.jumlah_tanggungan, 6) - 1
  return pools[Math.max(0, idx)]
}

function namaAnggota(id, slot) {
  const laki   = ['Wahyu','Agus','Hendra','Dian','Fajar','Rizki','Adi','Bayu','Irfan','Doni']
  const wanita = ['Sari','Dewi','Ani','Rani','Putri','Indah','Maya','Fitri','Rini','Nisa']
  const fam    = ['Santoso','Wijaya','Hidayat','Kurniawan','Prasetyo','Wibowo','Saputra','Nugroho','Susanto','Ismail']
  const isL  = (id + slot) % 2 === 0
  const first = isL ? laki[(id + slot) % laki.length] : wanita[(id + slot) % wanita.length]
  return first + ' ' + fam[(id * slot) % fam.length]
}

function riwayatBantuan(m) {
  const metode = ['Transfer Bank', 'Kantor Pos', 'Transfer Bank']
  const base   = Math.round(m.nominal * 0.75)
  return [
    { tahun:'2022', periode:'Jan – Des 2022', program:'Zakat Produktif DTSEN', nominal: base,                    metode: metode[0], status:'Tersalurkan', tanggal:'15 Des 2022' },
    { tahun:'2023', periode:'Jan – Jun 2023', program:'Zakat Konsumtif DTSEN', nominal: Math.round(base*0.5),   metode: metode[1], status:'Tersalurkan', tanggal:'20 Jun 2023' },
    { tahun:'2023', periode:'Jul – Des 2023', program:'Zakat Konsumtif DTSEN', nominal: Math.round(base*0.55),  metode: metode[0], status:'Tersalurkan', tanggal:'18 Des 2023' },
    { tahun:'2024', periode:'Jan – Jun 2024', program:'Zakat Produktif DTSEN', nominal: Math.round(m.nominal*0.5), metode: metode[2], status:'Tersalurkan', tanggal:'25 Jun 2024' },
    { tahun:'2024', periode:'Jul – Des 2024', program:'Zakat Produktif DTSEN', nominal: Math.round(m.nominal*0.5), metode: metode[0], status:'Proses',      tanggal:'— (dijadwalkan)' },
  ]
}

function totalKumulatif(m) {
  return riwayatBantuan(m).filter(r => r.status === 'Tersalurkan').reduce((a, b) => a + b.nominal, 0)
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
  width:45%;
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
</style>
