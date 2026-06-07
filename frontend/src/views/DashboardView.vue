<template>
  <AppLayout>
    <div style="display:flex;flex-direction:column;gap:24px;">

      <!-- Header -->
      <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap;">
        <div>
          <h2 style="font-size:1.5rem;font-weight:800;color:#1e293b;margin:0 0 4px;">Dashboard</h2>
          <p style="font-size:13px;color:#64748b;margin:0;">
            Selamat datang, <strong>{{ authStore.user?.name || 'Pengguna' }}</strong>
            <span style="margin-left:8px;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:600;"
              :style="roleBadgeStyle">{{ authStore.user?.role || 'operator' }}</span>
          </p>
        </div>
        <Button icon="pi pi-refresh" label="Perbarui" outlined size="small" :loading="loading" @click="loadData" />
      </div>

      <!-- Stat Cards -->
      <div class="grid-4" style="display:grid;gap:16px;">
        <div
          v-for="stat in statCards" :key="stat.label"
          style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:22px;box-shadow:0 1px 4px rgba(0,0,0,0.05);"
        >
          <div :style="{ width:'44px', height:'44px', borderRadius:'12px', background:stat.iconBg, display:'flex', alignItems:'center', justifyContent:'center', marginBottom:'14px' }">
            <i :class="stat.icon" :style="{ color:stat.iconColor, fontSize:'18px' }"></i>
          </div>
          <p style="font-size:1.5rem;font-weight:800;color:#1e293b;margin:0 0 3px;">{{ stat.value }}</p>
          <p style="font-size:13px;font-weight:600;color:#374151;margin:0 0 2px;">{{ stat.label }}</p>
          <p style="font-size:11px;color:#94a3b8;margin:0;">{{ stat.sub }}</p>
        </div>
      </div>

      <!-- Charts row 1 -->
      <div style="display:grid;grid-template-columns:1fr 2fr;gap:16px;" class="chart-row-1">
        <div style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:22px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
          <p style="font-size:13px;font-weight:700;color:#374151;margin:0 0 16px;">Gender Penerima</p>
          <Chart type="pie" :data="genderChartData" :options="pieOpts" style="height:220px;" />
        </div>
        <div style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:22px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
          <p style="font-size:13px;font-weight:700;color:#374151;margin:0 0 16px;">Tren Penyaluran Tahunan</p>
          <Chart type="bar" :data="trendChartData" :options="barOpts" style="height:220px;" />
        </div>
      </div>

      <!-- Charts row 2 -->
      <div style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:22px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
        <p style="font-size:13px;font-weight:700;color:#374151;margin:0 0 16px;">Penyaluran per Bidang Program</p>
        <Chart type="bar" :data="bidangChartData" :options="hBarOpts" style="height:280px;" />
      </div>

      <!-- Quick nav -->
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;" class="quick-nav">
        <div
          v-for="nav in quickNav" :key="nav.label"
          style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:20px;box-shadow:0 1px 4px rgba(0,0,0,0.05);cursor:pointer;transition:box-shadow 0.2s;"
          @click="$router.push(nav.to)"
          @mouseenter="e=>e.currentTarget.style.boxShadow='0 4px 16px rgba(0,0,0,0.1)'"
          @mouseleave="e=>e.currentTarget.style.boxShadow='0 1px 4px rgba(0,0,0,0.05)'"
        >
          <div :style="{ width:'40px', height:'40px', borderRadius:'10px', background:nav.iconBg, display:'flex', alignItems:'center', justifyContent:'center', marginBottom:'12px' }">
            <i :class="nav.icon" :style="{ color:nav.iconColor, fontSize:'17px' }"></i>
          </div>
          <p style="font-size:14px;font-weight:700;color:#1e293b;margin:0 0 2px;">{{ nav.label }}</p>
          <p style="font-size:12px;color:#94a3b8;margin:0;">{{ nav.desc }}</p>
        </div>
      </div>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Button    from 'primevue/button'
import Chart     from 'primevue/chart'
import AppLayout from '@/components/layout/AppLayout.vue'
import ReportService from '@/services/report'
import { useAuthStore } from '@/stores/auth'
import { formatRupiah } from '@/utils/formatter'

const authStore = useAuthStore()
const loading   = ref(false)
const summary   = ref({ total_penyaluran:0, penerima_manfaat:0, nasional:0, provinsi:0, kabkota:0 })
const gender    = ref({ male_count:0, female_count:0 })
const bidang    = ref([])
const trend     = ref([])

async function loadData() {
  loading.value = true
  try {
    const [s, g, b, t] = await Promise.all([
      ReportService.getHomeSummary(),
      ReportService.getByGender({}),
      ReportService.getByBidang({}),
      ReportService.getTimeseries({}),
    ])
    summary.value = s
    gender.value  = g
    bidang.value  = b
    trend.value   = t
  } finally {
    loading.value = false
  }
}
onMounted(loadData)

const roleBadgeStyle = computed(() => {
  const map = {
    admin:    { background:'#fef9c3', color:'#b45309' },
    operator: { background:'#dcfce7', color:'#15803d' },
    analis:   { background:'#dbeafe', color:'#1d4ed8' },
  }
  return map[authStore.user?.role] || map.operator
})

const statCards = computed(() => [
  { label:'Total Penyaluran', value:formatRupiah(summary.value.total_penyaluran||0), sub:'Seluruh LAZ',          icon:'pi pi-wallet',   iconBg:'#f0fdf4', iconColor:'#16a34a' },
  { label:'Penerima Manfaat', value:(summary.value.penerima_manfaat||0).toLocaleString('id-ID'), sub:'Mustahik unik', icon:'pi pi-users',  iconBg:'#eff6ff', iconColor:'#2563eb' },
  { label:'LAZ Terdaftar',    value:((summary.value.nasional||0)+(summary.value.provinsi||0)+(summary.value.kabkota||0)).toLocaleString('id-ID'), sub:'Nasional+Provinsi+Kab', icon:'pi pi-building', iconBg:'#faf5ff', iconColor:'#7c3aed' },
  { label:'Bidang Program',   value:(bidang.value.length||0)+'', sub:'Kategori aktif', icon:'pi pi-list', iconBg:'#fff7ed', iconColor:'#ea580c' },
])

const genderChartData = computed(() => ({
  labels: ['Laki-laki','Perempuan'],
  datasets: [{ data:[gender.value.male_count||0, gender.value.female_count||0], backgroundColor:['#3b82f6','#f472b6'], borderWidth:0 }]
}))
const trendChartData = computed(() => ({
  labels: trend.value.map(d=>d.tahun),
  datasets: [
    { label:'Bantuan Langsung',      data:trend.value.map(d=>d.Bantuan_Langsung||0),      backgroundColor:'#16a34a' },
    { label:'Bantuan Tidak Langsung',data:trend.value.map(d=>d.Bantuan_Tidak_Langsung||0),backgroundColor:'#f59e0b' },
  ]
}))
const bidangChartData = computed(() => ({
  labels: bidang.value.map(d=>d.bidang_label),
  datasets:[{ label:'Total Penyaluran (Rp)', data:bidang.value.map(d=>d.total_penyaluran||0), backgroundColor:'rgba(22,163,74,0.75)', borderRadius:4 }]
}))

const pieOpts  = { plugins:{ legend:{ position:'bottom' } }, responsive:true, maintainAspectRatio:false }
const barOpts  = { plugins:{ legend:{ position:'bottom' } }, responsive:true, maintainAspectRatio:false, scales:{ y:{ ticks:{ callback:v=>formatRupiah(v) } } } }
const hBarOpts = { indexAxis:'y', plugins:{ legend:{ display:false } }, responsive:true, maintainAspectRatio:false, scales:{ x:{ ticks:{ callback:v=>formatRupiah(v) } } } }

const quickNav = [
  { label:'Data Mustahik', desc:'Lihat & filter daftar penerima', to:'/mustahik', icon:'pi pi-users',    iconBg:'#eff6ff', iconColor:'#2563eb' },
  { label:'Laporan',       desc:'Analitik & grafik penyaluran',    to:'/report',   icon:'pi pi-chart-bar', iconBg:'#f0fdf4', iconColor:'#16a34a' },
  { label:'Peta Sebaran',  desc:'Visualisasi peta Indonesia',      to:'/',         icon:'pi pi-map',      iconBg:'#fff7ed', iconColor:'#ea580c' },
]
</script>

<style scoped>
.grid-4 { grid-template-columns: repeat(4,1fr); }
.chart-row-1 { grid-template-columns: 1fr 2fr; }
.quick-nav   { grid-template-columns: repeat(3,1fr); }
@media (max-width:1024px) {
  .grid-4      { grid-template-columns: repeat(2,1fr); }
  .chart-row-1 { grid-template-columns: 1fr; }
}
@media (max-width:640px) {
  .grid-4    { grid-template-columns: 1fr 1fr; }
  .quick-nav { grid-template-columns: 1fr; }
}
</style>
