<template>
  <AppLayout>
    <!-- Wrapper utama: position relative agar watermark absolute di dalamnya -->
    <div style="position:relative; display:flex; flex-direction:column; gap:24px;">

      <!-- ===== WATERMARK BACKGROUND ===== -->
      <div
        aria-hidden="true"
        style="
          position: absolute;
          inset: 0;
          z-index: 0;
          pointer-events: none;
          overflow: hidden;
          user-select: none;
          -webkit-user-select: none;
        "
      >
        <div
          style="
            position: absolute;
            top: -30%;
            left: -30%;
            width: 160%;
            height: 160%;
            display: flex;
            flex-wrap: wrap;
            align-content: flex-start;
            transform: rotate(-35deg);
            transform-origin: center center;
          "
        >
          <div
            v-for="i in 60"
            :key="i"
            style="
              display: block;
              width: 50%;
              padding: 28px 0;
              text-align: center;
              font-size: 12px;
              font-weight: 700;
              letter-spacing: 0.1em;
              text-transform: uppercase;
              color: rgba(15, 23, 42, 0.10);
              white-space: nowrap;
              font-family: Inter, sans-serif;
              line-height: 1;
            "
          >
            DO NOT COPY &nbsp;&bull;&nbsp; {{ userEmail }}
          </div>
        </div>
      </div>
      <!-- ===== END WATERMARK ===== -->

      <!-- Semua konten di z-index 1 agar di atas watermark -->
      <div style="position:relative; z-index:1; display:flex; flex-direction:column; gap:24px;">

        <!-- Header -->
        <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap;">
          <div>
            <h2 style="font-size:1.5rem;font-weight:800;color:#1e293b;margin:0 0 4px;">Dashboard</h2>
            <p style="font-size:13px;color:#64748b;margin:0;">
              Selamat datang, <strong>{{ authStore.user?.user_fullname || authStore.user?.nama_lengkap || 'Pengguna' }}</strong>
              <span style="margin-left:8px;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:600;"
                :style="roleBadgeStyle">{{ authStore.user?.user_grup || authStore.user?.jabatan || 'operator' }}</span>
            </p>
            <p style="font-size:11px;color:#94a3b8;margin:4px 0 0;">
              Wilayah: <strong style="color:#0f172a;">{{ authStore.user?.wilayah_label || 'Seluruh Indonesia' }}</strong>
              &nbsp;·&nbsp; Data mustahik desil 1–4 · Tahun 2024
            </p>
          </div>
          <span style="background:#fef3c7;color:#92400e;padding:4px 12px;border-radius:8px;font-size:11px;font-weight:600;">PROTOTYPE · Data Simulasi</span>
        </div>

        <!-- Stat Cards -->
        <div class="grid-4">
          <div v-for="stat in statCards" :key="stat.label" class="stat-card">
            <div :style="{ width:'44px', height:'44px', borderRadius:'12px', background:stat.iconBg, display:'flex', alignItems:'center', justifyContent:'center', marginBottom:'14px' }">
              <i :class="stat.icon" :style="{ color:stat.iconColor, fontSize:'18px' }"></i>
            </div>
            <p style="font-size:1.5rem;font-weight:800;color:#1e293b;margin:0 0 3px;">{{ stat.value }}</p>
            <p style="font-size:13px;font-weight:600;color:#374151;margin:0 0 2px;">{{ stat.label }}</p>
            <p style="font-size:11px;color:#94a3b8;margin:0;">{{ stat.sub }}</p>
          </div>
        </div>

        <!-- Desil breakdown cards -->
        <div>
          <p style="font-size:13px;font-weight:700;color:#374151;margin:0 0 12px;">Distribusi Mustahik per Desil</p>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;" class="desil-grid">
            <div v-for="d in stats.desil_breakdown" :key="d.desil"
              style="border-radius:14px;padding:18px;text-align:center;"
              :style="{ background:DESIL_COLORS[d.desil].bg, border:`1px solid ${DESIL_COLORS[d.desil].text}22` }">
              <p style="font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;margin:0 0 6px;" :style="{color:DESIL_COLORS[d.desil].text}">Desil {{ d.desil }}</p>
              <p style="font-size:2rem;font-weight:900;margin:0 0 2px;" :style="{color:DESIL_COLORS[d.desil].text}">{{ d.jumlah }}</p>
              <p style="font-size:11px;color:#64748b;margin:0 0 6px;">mustahik</p>
              <p style="font-size:12px;font-weight:600;margin:0;" :style="{color:DESIL_COLORS[d.desil].text}">{{ formatRupiah(d.total_nominal) }}</p>
            </div>
          </div>
        </div>

        <!-- Charts row -->
        <div style="display:grid;grid-template-columns:1fr 2fr;gap:16px;" class="chart-row">
          <!-- Gender Pie -->
          <div class="card-box">
            <p style="font-size:13px;font-weight:700;color:#374151;margin:0 0 16px;">Gender Penerima</p>
            <Chart type="pie" :data="genderChartData" :options="pieOpts" style="height:200px;" />
            <div style="display:flex;gap:16px;justify-content:center;margin-top:12px;">
              <span style="font-size:12px;color:#374151;"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#3b82f6;margin-right:5px;"></span>L: {{ stats.by_gender.m }}</span>
              <span style="font-size:12px;color:#374151;"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#f472b6;margin-right:5px;"></span>P: {{ stats.by_gender.f }}</span>
            </div>
          </div>
          <!-- Desil Bar -->
          <div class="card-box">
            <p style="font-size:13px;font-weight:700;color:#374151;margin:0 0 16px;">Jumlah Mustahik per Desil</p>
            <Chart type="bar" :data="desilBarData" :options="barOpts" style="height:200px;" />
          </div>
        </div>

        <!-- Sebaran Wilayah -->
        <div class="card-box">
          <p style="font-size:13px;font-weight:700;color:#374151;margin:0 0 16px;">
            Sebaran Mustahik
            <span style="font-weight:400;color:#94a3b8;">
              per {{ wilayahGroupLabel }}
            </span>
          </p>
          <div v-if="stats.by_provinsi.length === 0" style="text-align:center;padding:32px;color:#94a3b8;font-size:13px;">
            Tidak ada data mustahik di wilayah ini.
          </div>
          <div v-else style="display:flex;gap:16px;flex-wrap:wrap;">
            <div v-for="p in stats.by_provinsi" :key="p.nama"
              style="flex:1;min-width:160px;background:#f8fafc;border-radius:10px;padding:14px;border:1px solid #e2e8f0;">
              <p style="font-size:12px;color:#64748b;margin:0 0 4px;">{{ p.nama }}</p>
              <p style="font-size:1.4rem;font-weight:800;color:#1e293b;margin:0;">{{ p.jumlah }}</p>
              <div style="margin-top:8px;background:#e2e8f0;border-radius:4px;height:6px;">
                <div :style="{ width: stats.total_mustahik ? (p.jumlah/stats.total_mustahik*100)+'%' : '0%', height:'6px', borderRadius:'4px', background:'#3b82f6' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick nav -->
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;" class="quick-nav">
          <div v-for="nav in quickNav" :key="nav.label" class="nav-card" @click="$router.push(nav.to)">
            <div :style="{ width:'40px', height:'40px', borderRadius:'10px', background:nav.iconBg, display:'flex', alignItems:'center', justifyContent:'center', marginBottom:'12px' }">
              <i :class="nav.icon" :style="{ color:nav.iconColor, fontSize:'17px' }"></i>
            </div>
            <p style="font-size:14px;font-weight:700;color:#1e293b;margin:0 0 2px;">{{ nav.label }}</p>
            <p style="font-size:12px;color:#94a3b8;margin:0;">{{ nav.desc }}</p>
          </div>
        </div>

      </div>
      <!-- end z-index:1 wrapper -->

    </div>
  </AppLayout>
</template>

<script setup>
import { computed } from 'vue'
import Chart       from 'primevue/chart'
import AppLayout   from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { formatRupiah }  from '@/utils/formatter'
import { DESIL_COLORS, getMockByWilayah, buildSummaryStats } from '@/data/mockMustahik'

const authStore = useAuthStore()

/**
 * Ambil email user dari semua kemungkinan field.
 * Berdasarkan auth_service.py:
 *   - tuser  → field: email
 *   - dtsen  → field: email
 * Keduanya sama-sama 'email', tapi kita cek semua fallback untuk keamanan.
 */
const userEmail = computed(() => {
  const u = authStore.user
  if (!u) return 'CONFIDENTIAL'
  return (
    u.email        ||
    u.tuser_email  ||
    u.user_email   ||
    u.username     ||
    'CONFIDENTIAL'
  )
})

// ── Data ter-filter berdasarkan wilayah user yang login ──────────────────────
const filteredData = computed(() => getMockByWilayah(authStore.userWilayah))
const stats        = computed(() => buildSummaryStats(filteredData.value))

// Label grup sebaran
const wilayahGroupLabel = computed(() => {
  const w = authStore.userWilayah
  if (!w || w.level === 'provinsi') return 'Provinsi'
  if (w.level === 'kab_kota')       return 'Kecamatan'
  return 'Wilayah'
})

const roleBadgeStyle = computed(() => {
  const role = authStore.user?.user_grup || authStore.user?.jabatan || ''
  const map = {
    admin:    { background:'#fef9c3', color:'#b45309' },
    operator: { background:'#dcfce7', color:'#15803d' },
    analis:   { background:'#dbeafe', color:'#1d4ed8' },
  }
  return map[role] || map.operator
})

const statCards = computed(() => [
  { label:'Total Mustahik',     value: stats.value.total_mustahik.toLocaleString('id-ID'),       sub:'Desil 1–4 di wilayah ini', icon:'pi pi-users',     iconBg:'#eff6ff', iconColor:'#2563eb' },
  { label:'Total KK',           value: stats.value.total_kk.toLocaleString('id-ID'),             sub:'Kepala Keluarga',          icon:'pi pi-home',      iconBg:'#f0fdf4', iconColor:'#16a34a' },
  { label:'Total Penyaluran',   value: formatRupiah(stats.value.total_nominal),                  sub:'Nilai bantuan',            icon:'pi pi-wallet',    iconBg:'#faf5ff', iconColor:'#7c3aed' },
  { label:'Wilayah Terlayani',  value: stats.value.by_provinsi.length + '',                      sub: authStore.user?.wilayah_label || 'Seluruh Indonesia', icon:'pi pi-map-marker', iconBg:'#fff7ed', iconColor:'#ea580c' },
])

const genderChartData = computed(() => ({
  labels: ['Laki-laki','Perempuan'],
  datasets: [{ data:[stats.value.by_gender.m, stats.value.by_gender.f], backgroundColor:['#3b82f6','#f472b6'], borderWidth:0 }],
}))

const desilBarData = computed(() => ({
  labels: stats.value.desil_breakdown.map(d => 'Desil '+d.desil),
  datasets: [{
    label: 'Jumlah Mustahik',
    data: stats.value.desil_breakdown.map(d => d.jumlah),
    backgroundColor: ['#ef4444','#f97316','#eab308','#22c55e'],
    borderRadius: 6,
  }],
}))

const pieOpts = { plugins:{ legend:{ display:false } }, responsive:true, maintainAspectRatio:false }
const barOpts = {
  plugins:{ legend:{ display:false } },
  responsive:true, maintainAspectRatio:false,
  scales:{ y:{ beginAtZero:true, ticks:{ precision:0 } } },
}

const quickNav = [
  { label:'Data Mustahik', desc:'Lihat & filter daftar penerima', to:'/mustahik',  icon:'pi pi-users',  iconBg:'#eff6ff', iconColor:'#2563eb' },
  { label:'Cari Data',     desc:'Pencarian mustahik & filter NIK', to:'/cari-data', icon:'pi pi-search', iconBg:'#f0fdf4', iconColor:'#16a34a' },
  { label:'Beranda',       desc:'Kembali ke halaman publik',       to:'/',          icon:'pi pi-globe',  iconBg:'#fff7ed', iconColor:'#ea580c' },
]
</script>

<style scoped>
.grid-4  { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }
.desil-grid { }
.chart-row { grid-template-columns:1fr 2fr; }
.quick-nav { grid-template-columns:repeat(3,1fr); }
.stat-card {
  background:white; border-radius:16px; border:1px solid #f1f5f9;
  padding:22px; box-shadow:0 1px 4px rgba(0,0,0,0.05);
}
.card-box {
  background:white; border-radius:16px; border:1px solid #f1f5f9;
  padding:22px; box-shadow:0 1px 4px rgba(0,0,0,0.05);
}
.nav-card {
  background:white; border-radius:16px; border:1px solid #f1f5f9;
  padding:20px; box-shadow:0 1px 4px rgba(0,0,0,0.05);
  cursor:pointer; transition:box-shadow 0.2s;
}
.nav-card:hover { box-shadow:0 4px 16px rgba(0,0,0,0.1); }
@media (max-width:1024px) {
  .grid-4    { grid-template-columns:repeat(2,1fr); }
  .chart-row { grid-template-columns:1fr; }
  .desil-grid { grid-template-columns:repeat(2,1fr) !important; }
}
@media (max-width:640px) {
  .grid-4    { grid-template-columns:1fr 1fr; }
  .quick-nav { grid-template-columns:1fr; }
  .desil-grid { grid-template-columns:repeat(2,1fr) !important; }
}
</style>
