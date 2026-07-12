<template>
  <AppLayout>
    <div style="display:flex;flex-direction:column;gap:20px;">

      <!-- Back -->
      <button @click="$router.back()" style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border:1px solid #e2e8f0;border-radius:8px;background:white;font-size:13px;font-weight:600;cursor:pointer;color:#374151;width:fit-content;">
        <i class="pi pi-arrow-left" style="font-size:11px;"></i> Kembali
      </button>

      <!-- Loading -->
      <div v-if="loading" style="text-align:center;padding:60px;">
        <i class="pi pi-spin pi-spinner" style="font-size:32px;color:#cbd5e1;"></i>
        <p style="color:#94a3b8;margin-top:12px;font-size:13px;">Memuat data…</p>
      </div>

      <!-- Error / Not found -->
      <div v-else-if="!data" style="text-align:center;padding:60px 20px;background:white;border-radius:14px;border:1px solid #f1f5f9;">
        <i class="pi pi-user-minus" style="font-size:40px;color:#cbd5e1;"></i>
        <p style="color:#64748b;margin:12px 0 0;">Data anggota tidak ditemukan</p>
        <p style="color:#94a3b8;font-size:12px;margin-top:4px;">NIK: {{ route.params.nik }}</p>
      </div>

      <template v-else>

        <!-- ===== HEADER IDENTITY ===== -->
        <div style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:28px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
          <div style="display:flex;align-items:flex-start;gap:20px;flex-wrap:wrap;">
            <!-- Avatar -->
            <div :style="{
              width:'80px', height:'80px', borderRadius:'16px',
              background: isLaki ? '#eff6ff' : '#fdf2f8',
              display:'flex', alignItems:'center', justifyContent:'center',
              flexShrink:0, border: '2px solid ' + (isLaki ? '#bfdbfe' : '#fbcfe8')
            }">
              <i class="pi pi-user" :style="{ fontSize:'32px', color: isLaki ? '#2563eb' : '#db2777' }"></i>
            </div>

            <div style="flex:1;min-width:0;">
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px;">
                <h2 style="font-size:1.25rem;font-weight:800;color:#1e293b;margin:0;">{{ data.nama ?? '-' }}</h2>
                <span v-if="data.jenis_kelamin" :style="{ padding:'3px 10px', borderRadius:'99px', fontSize:'11px', fontWeight:'700', background: isLaki?'#eff6ff':'#fdf2f8', color: isLaki?'#2563eb':'#db2777' }">
                  {{ isLaki ? 'Laki-laki' : 'Perempuan' }}
                </span>
                <span v-if="data.status_kawin" style="padding:3px 10px;border-radius:99px;font-size:11px;font-weight:700;background:#f0fdf4;color:#15803d;">
                  {{ statusKawinLabel(data.status_kawin) }}
                </span>
              </div>
              <p style="font-size:13px;color:#64748b;margin:0 0 4px;">NIK: <strong style="color:#374151;font-family:monospace;">{{ data.nomor_induk_kependudukan ?? '-' }}</strong></p>
              <p style="font-size:13px;color:#64748b;margin:0;">No. KK: <strong style="color:#374151;font-family:monospace;">{{ data.nomor_kartu_keluarga ?? '-' }}</strong></p>
            </div>

            <!-- Badge PBI -->
            <div style="display:flex;flex-direction:column;gap:6px;flex-shrink:0;">
              <span v-if="data.pbi_nas === '1'" style="padding:4px 12px;border-radius:99px;font-size:11px;font-weight:700;background:#fef3c7;color:#b45309;">
                <i class="pi pi-shield" style="font-size:10px;"></i> PBI Nasional
              </span>
              <span v-if="data.pbi_pemda === '1'" style="padding:4px 12px;border-radius:99px;font-size:11px;font-weight:700;background:#ede9fe;color:#6d28d9;">
                <i class="pi pi-shield" style="font-size:10px;"></i> PBI Pemda
              </span>
              <span v-if="data.pbi_nas !== '1' && data.pbi_pemda !== '1'" style="padding:4px 12px;border-radius:99px;font-size:11px;font-weight:600;background:#f1f5f9;color:#94a3b8;">
                Non PBI
              </span>
            </div>
          </div>
        </div>

        <!-- ===== GRID ROW 1: Data Pribadi + Alamat KTP ===== -->
        <div class="grid-2">

          <!-- Data Pribadi -->
          <div class="detail-card wm-card">
            <div class="wm-overlay" aria-hidden="true"><svg class="wm-svg" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="wm-a1" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><text x="10" y="40" font-family="Inter,sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text><text x="10" y="70" font-family="Inter,sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text></pattern></defs><rect width="100%" height="100%" fill="url(#wm-a1)" /></svg></div>
            <div style="position:relative;z-index:1;">
              <p class="section-title"><i class="pi pi-id-card"></i> Data Pribadi</p>
              <table class="info-table">
                <tbody>
                  <tr><td class="td-label">Tanggal Lahir</td><td class="td-value">{{ data.tanggal_lahir ?? '-' }}</td></tr>
                  <tr><td class="td-label">Jenis Kelamin</td><td class="td-value">{{ isLaki ? 'Laki-laki' : 'Perempuan' }}</td></tr>
                  <tr><td class="td-label">Status Kawin</td><td class="td-value">{{ statusKawinLabel(data.status_kawin) }}</td></tr>
                  <tr><td class="td-label">Hub. Keluarga</td><td class="td-value">{{ hubunganLabel(data.status_hubungan_keluarga) }}</td></tr>
                  <tr><td class="td-label">No. KK</td><td class="td-value" style="font-family:monospace;font-size:12px;">{{ data.nomor_kartu_keluarga ?? '-' }}</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Alamat KTP -->
          <div class="detail-card wm-card">
            <div class="wm-overlay" aria-hidden="true"><svg class="wm-svg" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="wm-a2" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><text x="10" y="40" font-family="Inter,sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text><text x="10" y="70" font-family="Inter,sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text></pattern></defs><rect width="100%" height="100%" fill="url(#wm-a2)" /></svg></div>
            <div style="position:relative;z-index:1;">
              <p class="section-title"><i class="pi pi-map-marker"></i> Alamat KTP</p>
              <table class="info-table">
                <tbody>
                  <tr><td class="td-label">Alamat</td><td class="td-value">{{ data.alamat_ktp ?? '-' }}</td></tr>
                  <tr><td class="td-label">RT / RW</td><td class="td-value">{{ data.rt_ktp ?? '-' }} / {{ data.rw_ktp ?? '-' }}</td></tr>
                  <tr><td class="td-label">Dusun</td><td class="td-value">{{ data.dusun_ktp ?? '-' }}</td></tr>
                  <tr><td class="td-label">Kel / Desa</td><td class="td-value">{{ data.kelurahan_desa_ktp ?? '-' }}</td></tr>
                  <tr><td class="td-label">Kecamatan</td><td class="td-value">{{ data.kecamatan_ktp ?? '-' }}</td></tr>
                  <tr><td class="td-label">Kab / Kota</td><td class="td-value">{{ data.kabupaten_kota_ktp ?? '-' }}</td></tr>
                  <tr><td class="td-label">Provinsi</td><td class="td-value">{{ data.provinsi_ktp ?? '-' }}</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ===== GRID ROW 2: Pendidikan + Pekerjaan ===== -->
        <div class="grid-2">

          <!-- Pendidikan -->
          <div class="detail-card wm-card">
            <div class="wm-overlay" aria-hidden="true"><svg class="wm-svg" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="wm-a3" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><text x="10" y="40" font-family="Inter,sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text><text x="10" y="70" font-family="Inter,sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text></pattern></defs><rect width="100%" height="100%" fill="url(#wm-a3)" /></svg></div>
            <div style="position:relative;z-index:1;">
              <p class="section-title"><i class="pi pi-book"></i> Pendidikan</p>
              <table class="info-table">
                <tbody>
                  <tr><td class="td-label">Partisipasi Sekolah</td><td class="td-value">{{ partisipasiLabel(data.partisipasi_sekolah) }}</td></tr>
                  <tr><td class="td-label">Jenjang Tertinggi</td><td class="td-value">{{ jenjangLabel(data.jenjang_tertinggi_yang_diduduki) }}</td></tr>
                  <tr><td class="td-label">Kelas Tertinggi</td><td class="td-value">{{ data.kelas_tertinggi_yang_diduduki != null ? 'Kelas ' + data.kelas_tertinggi_yang_diduduki : '-' }}</td></tr>
                  <tr><td class="td-label">Ijazah Tertinggi</td><td class="td-value">{{ ijazahLabel(data.ijazah_tertinggi_yang_dimiliki) }}</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Pekerjaan -->
          <div class="detail-card wm-card">
            <div class="wm-overlay" aria-hidden="true"><svg class="wm-svg" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="wm-a4" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><text x="10" y="40" font-family="Inter,sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text><text x="10" y="70" font-family="Inter,sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text></pattern></defs><rect width="100%" height="100%" fill="url(#wm-a4)" /></svg></div>
            <div style="position:relative;z-index:1;">
              <p class="section-title"><i class="pi pi-briefcase"></i> Pekerjaan &amp; Usaha</p>
              <table class="info-table">
                <tbody>
                  <tr><td class="td-label">Status Bekerja</td><td class="td-value">{{ statusBekerjaLabel(data.status_bekerja) }}</td></tr>
                  <tr><td class="td-label">Status dlm Pekerjaan</td><td class="td-value">{{ statusDalamPekerjaanLabel(data.status_dalam_pekerjaan_utama) }}</td></tr>
                  <tr><td class="td-label">Lapangan Usaha</td><td class="td-value">{{ lapanganUsahaLabel(data.lapangan_usaha_dari_pekerjaan_utama) }}</td></tr>
                  <tr><td class="td-label">Kepemilikan Usaha</td><td class="td-value">{{ kepemilikanUsahaLabel(data.kepemilikan_usaha) }}</td></tr>
                  <tr><td class="td-label">Jumlah Usaha</td><td class="td-value">{{ data.jumlah_usaha != null ? data.jumlah_usaha + ' usaha' : '-' }}</td></tr>
                  <tr><td class="td-label">Omzet Usaha/Bln</td><td class="td-value">{{ data.omzet_usaha_utama ? formatRupiah(data.omzet_usaha_utama) : '-' }}</td></tr>
                  <tr><td class="td-label">Pekerja Dibayar</td><td class="td-value">{{ data.jumlah_pekerja_yang_dibayar_dari_usaha_utama ?? '-' }} orang</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ===== DISABILITAS + KESEHATAN (full width) ===== -->
        <div class="detail-card wm-card">
          <div class="wm-overlay" aria-hidden="true"><svg class="wm-svg" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="wm-a5" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><text x="10" y="40" font-family="Inter,sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text><text x="10" y="70" font-family="Inter,sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text></pattern></defs><rect width="100%" height="100%" fill="url(#wm-a5)" /></svg></div>
          <div style="position:relative;z-index:1;">
            <p class="section-title"><i class="pi pi-heart"></i> Kesehatan &amp; Disabilitas</p>
            <div class="grid-3" style="gap:12px;">
              <div v-for="item in disabilitasItems" :key="item.label">
                <p style="font-size:11px;color:#94a3b8;font-weight:600;margin:0 0 4px;text-transform:uppercase;letter-spacing:.5px;">{{ item.label }}</p>
                <span :style="{
                  display:'inline-block', padding:'3px 10px', borderRadius:'99px',
                  fontSize:'12px', fontWeight:'700',
                  background: item.val==='1'||item.val===1 ? '#fef2f2' : '#f0fdf4',
                  color:       item.val==='1'||item.val===1 ? '#dc2626'  : '#15803d'
                }">
                  {{ item.val==='1'||item.val===1 ? 'Ada Hambatan' : 'Normal' }}
                </span>
              </div>
              <!-- Kondisi Gizi -->
              <div>
                <p style="font-size:11px;color:#94a3b8;font-weight:600;margin:0 0 4px;text-transform:uppercase;letter-spacing:.5px;">Kondisi Gizi</p>
                <span style="display:inline-block;padding:3px 10px;border-radius:99px;font-size:12px;font-weight:700;background:#fef3c7;color:#b45309;">
                  {{ giziLabel(data.kondisi_gizi) }}
                </span>
              </div>
              <!-- Penyakit Kronis -->
              <div>
                <p style="font-size:11px;color:#94a3b8;font-weight:600;margin:0 0 4px;text-transform:uppercase;letter-spacing:.5px;">Penyakit Kronis</p>
                <span :style="{
                  display:'inline-block', padding:'3px 10px', borderRadius:'99px',
                  fontSize:'12px', fontWeight:'700',
                  background: data.penyakit_kronis ? '#fef2f2' : '#f0fdf4',
                  color:       data.penyakit_kronis ? '#dc2626'  : '#15803d'
                }">
                  {{ penyakitKronisLabel(data.penyakit_kronis) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- ===== RINGKASAN BANSOS ===== -->
        <div class="detail-card">
          <p class="section-title"><i class="pi pi-wallet"></i> Status Bantuan Sosial</p>
          <div class="grid-3">
            <div class="stat-box" :style="{ background: data.pbi_nas==='1' ? '#fefce8' : '#f8fafc' }">
              <p class="stat-label">PBI Nasional</p>
              <p class="stat-val" :style="{ color: data.pbi_nas==='1' ? '#b45309' : '#94a3b8' }">
                {{ data.pbi_nas === '1' ? 'Terdaftar' : 'Tidak' }}
              </p>
            </div>
            <div class="stat-box" :style="{ background: data.pbi_pemda==='1' ? '#ede9fe' : '#f8fafc' }">
              <p class="stat-label">PBI Pemda</p>
              <p class="stat-val" :style="{ color: data.pbi_pemda==='1' ? '#6d28d9' : '#94a3b8' }">
                {{ data.pbi_pemda === '1' ? 'Terdaftar' : 'Tidak' }}
              </p>
            </div>
            <div class="stat-box" :style="{ background: data.id_pelanggan_pln ? '#f0fdf4' : '#f8fafc' }">
              <p class="stat-label">ID Pelanggan PLN</p>
              <p style="font-size:1rem;font-family:monospace;font-weight:900;margin:0;" :style="{ color: data.id_pelanggan_pln ? '#15803d' : '#94a3b8' }">
                {{ data.id_pelanggan_pln ?? 'Tidak ada' }}
              </p>
            </div>
          </div>
        </div>

      </template>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { fetchBaselineProvinsi } from '@/services/baselineService'

const route     = useRoute()
const authStore = useAuthStore()

const loading = ref(true)
const data    = ref(null)

const userIdentifier = computed(() => {
  const u = authStore.user
  if (!u) return 'CONFIDENTIAL'
  return u.email || u.tuser_email || u.notelp || u.user_id || 'CONFIDENTIAL'
})

async function loadData() {
  loading.value = true
  data.value = null
  const nik = route.params.nik

  try {
    const provinsiList = await fetchBaselineProvinsi()
    const firstProvinsi = provinsiList?.[0]?.kode

    if (!firstProvinsi) {
      console.error('[AnggotaDetail] Tidak ada provinsi yang dapat diakses')
      return
    }

    const res = await api.get('/baseline/anggota', {
      params: { provinsi: firstProvinsi, search: nik },
    })

    const items = res.data?.data ?? []
    data.value = items.find(
      r => r.nomor_induk_kependudukan === nik || r.nik === nik
    ) ?? items[0] ?? null

  } catch (e) {
    console.error('[AnggotaDetail] gagal load:', e)
  } finally {
    loading.value = false
  }
}

const isLaki = computed(() => {
  const v = (data.value?.jenis_kelamin ?? '').toString().toLowerCase()
  return v === 'l' || v === 'laki-laki' || v === '1' || v === 'm'
})

const disabilitasItems = computed(() => [
  { label: 'Penglihatan',       val: data.value?.penglihatan },
  { label: 'Pendengaran',       val: data.value?.pendengaran },
  { label: 'Berjalan / Tangga', val: data.value?.berjalan_atau_naik_tangga },
  { label: 'Tangan / Jari',     val: data.value?.menggunakan_tangan_jari },
  { label: 'Mengingat',         val: data.value?.mengingat_berkonsentrasi },
  { label: 'Mengurus Diri',     val: data.value?.mengurus_diri },
  { label: 'Komunikasi',        val: data.value?.berbicara_komunikasi },
  { label: 'Belajar',           val: data.value?.belajar_kemampuan_intelektual },
  { label: 'Perilaku',          val: data.value?.pengendalian_perilaku },
  { label: 'Kesedihan',         val: data.value?.kesedihan_depresi },
])

// ─── Label helpers ──────────────────────────────────────────
function statusKawinLabel(v) {
  return { '1':'Belum Kawin','2':'Kawin','3':'Cerai Hidup','4':'Cerai Mati' }[String(v)] ?? v ?? '-'
}
function hubunganLabel(v) {
  return {
    '1':'Kepala Keluarga','2':'Istri/Suami','3':'Anak',
    '4':'Menantu','5':'Cucu','6':'Orang Tua','7':'Mertua',
    '8':'Famili Lain','9':'Pembantu','10':'Lainnya'
  }[String(v)] ?? v ?? '-'
}
function partisipasiLabel(v) {
  return { '1':'Tidak/Belum Sekolah','2':'Masih Sekolah','3':'Tidak Sekolah Lagi' }[String(v)] ?? v ?? '-'
}
function jenjangLabel(v) {
  return {
    '0':'Tidak/Belum Sekolah','1':'SD/MI','2':'SMP/MTs','3':'SMA/MA/SMK',
    '4':'D1/D2/D3','5':'D4/S1','6':'S2','7':'S3'
  }[String(v)] ?? v ?? '-'
}
function ijazahLabel(v) {
  return {
    '0':'Tidak Ada Ijazah','1':'SD/MI','2':'SMP/MTs','3':'SMA/MA/SMK',
    '4':'D1/D2/D3','5':'D4/S1','6':'S2','7':'S3'
  }[String(v)] ?? v ?? '-'
}
function statusBekerjaLabel(v) {
  return {
    '1':'Bekerja','2':'Tidak Bekerja','3':'Ibu Rumah Tangga','4':'Sekolah','5':'Lainnya'
  }[String(v)] ?? v ?? '-'
}
function statusDalamPekerjaanLabel(v) {
  return {
    '1':'Berusaha Sendiri','2':'Berusaha Dibantu',
    '3':'Buruh/Karyawan','4':'Pekerja Bebas','5':'Pekerja Tak Dibayar'
  }[String(v)] ?? v ?? '-'
}
function lapanganUsahaLabel(v) {
  return {
    '1':'Pertanian','2':'Pertambangan','3':'Industri Pengolahan',
    '4':'Listrik/Gas/Air','5':'Konstruksi','6':'Perdagangan',
    '7':'Transportasi','8':'Keuangan','9':'Jasa'
  }[String(v)] ?? v ?? '-'
}
function kepemilikanUsahaLabel(v) {
  return { '1':'Milik Sendiri','2':'Bukan Milik Sendiri' }[String(v)] ?? v ?? '-'
}
function giziLabel(v) {
  return { '1':'Baik','2':'Kurang','3':'Buruk' }[String(v)] ?? v ?? '-'
}
function penyakitKronisLabel(v) {
  if (!v && v !== 0) return '-'
  return { '0':'Tidak Ada','1':'Satu Jenis','2':'Dua Jenis atau Lebih' }[String(v)] ?? 'Ada'
}
function formatRupiah(n) {
  if (!n && n !== 0) return '-'
  return 'Rp ' + Number(n).toLocaleString('id-ID')
}

onMounted(() => loadData())
</script>

<style scoped>
.grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.grid-3 { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
@media(max-width:768px) {
  .grid-2 { grid-template-columns:1fr; }
  .grid-3 { grid-template-columns:1fr; }
}
.detail-card {
  background:white; border-radius:14px; border:1px solid #f1f5f9;
  padding:22px; box-shadow:0 1px 4px rgba(0,0,0,0.04);
}
.wm-card { position:relative; overflow:hidden; }
.wm-overlay { position:absolute; inset:0; z-index:0; pointer-events:none; user-select:none; }
.wm-svg { display:block; width:100%; height:100%; }
.section-title {
  font-size:13px; font-weight:700; color:#374151;
  margin:0 0 14px; display:flex; align-items:center; gap:6px;
}
.info-table { width:100%; border-collapse:collapse; }
.info-table tr { border-bottom:1px solid #f8fafc; }
.info-table tr:last-child { border-bottom:none; }
.td-label { font-size:12px; color:#94a3b8; font-weight:500; padding:9px 4px; width:45%; vertical-align:top; }
.td-value { font-size:13px; color:#374151; font-weight:600; padding:9px 4px; text-align:right; }
.stat-box { border-radius:10px; padding:16px; }
.stat-label { font-size:11px; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:.5px; margin:0 0 4px; }
.stat-val { font-size:1.25rem; font-weight:900; margin:0; }
</style>
