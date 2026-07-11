<template>
  <LandingLayout>

    <!-- ======================================================
         HERO
    ======================================================= -->
    <section
      id="hero"
      style="
        min-height: 100vh;
        background: linear-gradient(135deg, #052e16 0%, #14532d 40%, #166534 70%, #15803d 100%);
        display: flex;
        align-items: center;
        position: relative;
        overflow: hidden;
        padding-top: 64px;
      "
    >
      <!-- decorative circles -->
      <div style="position:absolute;top:-80px;right:-80px;width:400px;height:400px;background:rgba(245,158,11,0.12);border-radius:50%;filter:blur(60px);pointer-events:none;"></div>
      <div style="position:absolute;bottom:-100px;left:-60px;width:320px;height:320px;background:rgba(74,222,128,0.1);border-radius:50%;filter:blur(50px);pointer-events:none;"></div>

      <div style="max-width:1280px;margin:0 auto;padding:80px 24px;width:100%;">
        <div class="hero-grid">

          <!-- LEFT -->
          <div>
            <!-- badge -->
            <div style="display:inline-flex;align-items:center;gap:6px;padding:5px 14px;border-radius:99px;background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.35);margin-bottom:20px;">
              <i class="pi pi-star-fill" style="font-size:10px;color:#f59e0b;"></i>
              <span style="font-size:12px;font-weight:600;color:#fcd34d;"> Data Tunggal Sosial dan Ekonomi Nasional</span>
            </div>

            <h1 style="font-size:clamp(2rem,4vw,3.25rem);font-weight:800;color:#fff;line-height:1.15;margin:0 0 20px;letter-spacing:-0.02em;">
              Sistem Informasi<br />
              <span style="color:#fbbf24;">Zakat</span><br />
              Nasional
            </h1>

            <p style="font-size:16px;color:#a7f3d0;line-height:1.7;max-width:480px;margin:0 0 32px;">
              Platform pemantauan penyaluran zakat berbasis data desil kemiskinan.
              Transparan, terukur, dan tepat sasaran.
            </p>

            <div style="display:flex;flex-wrap:wrap;gap:12px;">
              <button
                style="display:inline-flex;align-items:center;gap:8px;padding:12px 24px;border-radius:10px;background:#f59e0b;border:none;color:#fff;font-size:14px;font-weight:700;cursor:pointer;box-shadow:0 4px 14px rgba(245,158,11,0.4);transition:transform 0.15s;"
                @click="scrollTo('#stats')"
              >
                <i class="pi pi-chart-bar"></i> Lihat Statistik
              </button>
              <button
                style="display:inline-flex;align-items:center;gap:8px;padding:12px 24px;border-radius:10px;background:transparent;border:1.5px solid rgba(255,255,255,0.5);color:#fff;font-size:14px;font-weight:600;cursor:pointer;transition:background 0.15s;"
                @click="loginModal.open()"
              >
                <i class="pi pi-sign-in"></i> Masuk Sistem
              </button>
            </div>
          </div>

          <!-- RIGHT: stat cards -->
          <div class="hero-cards">
            <div
              v-for="stat in heroStats"
              :key="stat.label"
              style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.14);border-radius:16px;padding:20px;backdrop-filter:blur(8px);"
            >
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                <div style="width:32px;height:32px;border-radius:8px;background:rgba(245,158,11,0.2);display:flex;align-items:center;justify-content:center;">
                  <i :class="stat.icon" style="color:#fbbf24;font-size:13px;"></i>
                </div>
                <span style="font-size:11px;color:#a7f3d0;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">{{ stat.label }}</span>
              </div>
              <p style="font-size:1.6rem;font-weight:800;color:#fff;margin:0 0 4px;">{{ stat.value }}</p>
              <p style="font-size:11px;color:#6ee7b7;margin:0;">{{ stat.sub }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- scroll hint -->
      <div style="position:absolute;bottom:24px;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:4px;color:#6ee7b7;animation:bounce 2s infinite;">
        <span style="font-size:11px;">Gulir ke bawah</span>
        <i class="pi pi-angle-down" style="font-size:16px;"></i>
      </div>
    </section>

    <!-- ======================================================
         STATS
    ======================================================= -->
    <section id="stats" style="padding:80px 0;background:#f8fafc;">
      <div style="max-width:1280px;margin:0 auto;padding:0 24px;">

        <div style="text-align:center;margin-bottom:48px;">
          <span style="display:inline-block;padding:4px 14px;border-radius:99px;background:#dcfce7;color:#15803d;font-size:12px;font-weight:600;margin-bottom:12px;">Data Real-time</span>
          <h2 style="font-size:2rem;font-weight:800;color:#1e293b;margin:0 0 8px;">Statistik Nasional</h2>
          <p style="font-size:15px;color:#64748b;max-width:480px;margin:0 auto;">Agregat penyaluran zakat seluruh LAZ terdaftar di Indonesia.</p>
        </div>

        <div class="grid-4" style="display:grid;gap:16px;margin-bottom:40px;">
          <div
            v-for="stat in aggStats"
            :key="stat.label"
            style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:24px;box-shadow:0 1px 4px rgba(0,0,0,0.05);transition:box-shadow 0.2s;"
          >
            <div :style="{ width:'44px', height:'44px', borderRadius:'12px', background:stat.iconBg, display:'flex', alignItems:'center', justifyContent:'center', marginBottom:'16px' }">
              <i :class="stat.icon" :style="{ color:stat.iconColor, fontSize:'18px' }"></i>
            </div>
            <p style="font-size:1.6rem;font-weight:800;color:#1e293b;margin:0 0 4px;">{{ stat.value }}</p>
            <p style="font-size:14px;font-weight:600;color:#374151;margin:0 0 4px;">{{ stat.label }}</p>
            <p style="font-size:12px;color:#94a3b8;margin:0;">{{ stat.sub }}</p>
          </div>
        </div>

        <div class="grid-3" style="display:grid;gap:16px;">
          <div style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:20px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
            <p style="font-size:13px;font-weight:700;color:#374151;margin:0 0 16px;">Gender Penerima</p>
            <Chart type="doughnut" :data="genderChartData" :options="doughnutOpts" style="height:170px;" />
          </div>
          <div style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:20px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
            <p style="font-size:13px;font-weight:700;color:#374151;margin:0 0 16px;">Penyaluran per Bidang</p>
            <Chart type="bar" :data="bidangChartData" :options="barOpts" style="height:170px;" />
          </div>
          <div style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:20px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
            <p style="font-size:13px;font-weight:700;color:#374151;margin:0 0 16px;">Tren Penyaluran Tahunan</p>
            <Chart type="line" :data="trendChartData" :options="lineOpts" style="height:170px;" />
          </div>
        </div>
      </div>
    </section>

    <!-- ======================================================
         PETA
    ======================================================= -->
    <section id="map" style="padding:80px 0;background:white;">
      <div style="max-width:1280px;margin:0 auto;padding:0 24px;">

        <div style="text-align:center;margin-bottom:48px;">
          <span style="display:inline-block;padding:4px 14px;border-radius:99px;background:#dbeafe;color:#1d4ed8;font-size:12px;font-weight:600;margin-bottom:12px;">Sebaran Wilayah</span>
          <h2 style="font-size:2rem;font-weight:800;color:#1e293b;margin:0 0 8px;">Peta Sebaran Mustahik</h2>
          <p style="font-size:15px;color:#64748b;max-width:480px;margin:0 auto;">Distribusi penerima manfaat zakat per provinsi seluruh Indonesia.</p>
        </div>

        <div style="display:flex;justify-content:center;margin-bottom:24px;">
          <div style="display:inline-flex;background:#f1f5f9;border-radius:10px;padding:4px;gap:4px;">
            <button
              v-for="opt in metricOptions"
              :key="opt.value"
              :style="{
                padding: '8px 20px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s',
                background: mapMetric === opt.value ? 'white' : 'transparent',
                color: mapMetric === opt.value ? '#15803d' : '#64748b',
                boxShadow: mapMetric === opt.value ? '0 1px 4px rgba(0,0,0,0.1)' : 'none'
              }"
              @click="mapMetric = opt.value"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <div style="border-radius:16px;overflow:hidden;border:1px solid #e2e8f0;">
          <IndonesiaMap :map-data="mapData" :metric="mapMetric" height="480px" />
        </div>

        <div class="grid-2" style="display:grid;gap:24px;margin-top:32px;">
          <div style="background:#f8fafc;border-radius:16px;padding:24px;">
            <h3 style="font-size:14px;font-weight:700;color:#374151;margin:0 0 16px;display:flex;align-items:center;gap:8px;">
              <i class="pi pi-users" style="color:#3b82f6;"></i> Top 5 Mustahik Terbanyak
            </h3>
            <div v-for="(prov, i) in topProvinces" :key="prov.provinsi_nama" style="margin-bottom:12px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                <div style="display:flex;align-items:center;gap:8px;">
                  <span style="width:20px;height:20px;border-radius:50%;background:#dbeafe;color:#1d4ed8;font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;">{{ i+1 }}</span>
                  <span style="font-size:13px;font-weight:500;color:#374151;">{{ prov.provinsi_nama }}</span>
                </div>
                <span style="font-size:12px;color:#64748b;font-weight:600;">{{ prov.mustahik?.toLocaleString('id-ID') }}</span>
              </div>
              <div style="height:6px;background:#e2e8f0;border-radius:99px;overflow:hidden;">
                <div :style="{ width: prov.pct+'%', height:'100%', background:'#3b82f6', borderRadius:'99px', transition:'width 0.5s' }"></div>
              </div>
            </div>
          </div>

          <div style="background:#f8fafc;border-radius:16px;padding:24px;">
            <h3 style="font-size:14px;font-weight:700;color:#374151;margin:0 0 16px;display:flex;align-items:center;gap:8px;">
              <i class="pi pi-wallet" style="color:#16a34a;"></i> Top 5 Penyaluran Terbesar
            </h3>
            <div v-for="(prov, i) in topProvincesByPenyaluran" :key="prov.provinsi_nama" style="margin-bottom:12px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                <div style="display:flex;align-items:center;gap:8px;">
                  <span style="width:20px;height:20px;border-radius:50%;background:#dcfce7;color:#15803d;font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;">{{ i+1 }}</span>
                  <span style="font-size:13px;font-weight:500;color:#374151;">{{ prov.provinsi_nama }}</span>
                </div>
                <span style="font-size:12px;color:#64748b;font-weight:600;">{{ formatRupiah(prov.penyaluran) }}</span>
              </div>
              <div style="height:6px;background:#e2e8f0;border-radius:99px;overflow:hidden;">
                <div :style="{ width: prov.pct_penyaluran+'%', height:'100%', background:'#16a34a', borderRadius:'99px', transition:'width 0.5s' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ======================================================
         PROGRAM / BIDANG
    ======================================================= -->
    <section id="program" style="padding:80px 0;background:#f8fafc;">
      <div style="max-width:1280px;margin:0 auto;padding:0 24px;">

        <div style="text-align:center;margin-bottom:48px;">
          <span style="display:inline-block;padding:4px 14px;border-radius:99px;background:#fef9c3;color:#b45309;font-size:12px;font-weight:600;margin-bottom:12px;">Kategori Penyaluran</span>
          <h2 style="font-size:2rem;font-weight:800;color:#1e293b;margin:0 0 8px;">Program Bidang Zakat</h2>
          <p style="font-size:15px;color:#64748b;max-width:480px;margin:0 auto;">Penyaluran berdasarkan kategori bidang program BAZNAS.</p>
        </div>

        <div class="grid-3" style="display:grid;gap:16px;">
          <div
            v-for="(bidang, i) in bidangProgram"
            :key="bidang.bidang_label"
            style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:24px;box-shadow:0 1px 4px rgba(0,0,0,0.05);transition:box-shadow 0.2s;"
          >
            <div :style="{ width:'44px', height:'44px', borderRadius:'12px', background:bidangColors[i%bidangColors.length].bg, display:'flex', alignItems:'center', justifyContent:'center', marginBottom:'14px' }">
              <i :class="bidangIcons[i%bidangIcons.length]" :style="{ color:bidangColors[i%bidangColors.length].icon, fontSize:'18px' }"></i>
            </div>
            <h3 style="font-size:14px;font-weight:700;color:#1e293b;margin:0 0 4px;">{{ bidang.bidang_label }}</h3>
            <p style="font-size:1.3rem;font-weight:800;color:#15803d;margin:0 0 12px;">{{ formatRupiah(bidang.total_penyaluran||0) }}</p>
            <div>
              <div style="display:flex;justify-content:space-between;font-size:11px;color:#94a3b8;margin-bottom:4px;">
                <span>Porsi dari total</span>
                <span style="font-weight:600;color:#374151;">{{ bidang.pct?.toFixed(1)||0 }}%</span>
              </div>
              <div style="height:5px;background:#f1f5f9;border-radius:99px;overflow:hidden;">
                <div :style="{ width: (bidang.pct||0)+'%', height:'100%', background:'#16a34a', borderRadius:'99px' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ======================================================
         TENTANG
    ======================================================= -->
    <section id="tentang" style="padding:80px 0;background:white;">
      <div style="max-width:1280px;margin:0 auto;padding:0 24px;">
        <div class="tentang-grid">

          <div>
            <span style="display:inline-block;padding:4px 14px;border-radius:99px;background:#f1f5f9;color:#475569;font-size:12px;font-weight:600;margin-bottom:16px;">Tentang Sistem</span>
            <h2 style="font-size:2rem;font-weight:800;color:#1e293b;margin:0 0 14px;">Mengapa DTSEN?</h2>
            <p style="font-size:15px;color:#64748b;line-height:1.7;margin:0 0 28px;max-width:480px;">
              DTSEN mengintegrasikan data penerima manfaat zakat dari seluruh LAZ terdaftar dengan data
              desil kemiskinan — memastikan penyaluran tepat sasaran.
            </p>
            <div style="display:flex;flex-direction:column;gap:16px;">
              <div v-for="feat in features" :key="feat.title" style="display:flex;gap:14px;align-items:flex-start;">
                <div style="width:40px;height:40px;border-radius:10px;background:#f0fdf4;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                  <i :class="feat.icon" style="color:#15803d;font-size:15px;"></i>
                </div>
                <div>
                  <h4 style="font-size:14px;font-weight:700;color:#1e293b;margin:0 0 3px;">{{ feat.title }}</h4>
                  <p style="font-size:13px;color:#64748b;margin:0;line-height:1.5;">{{ feat.desc }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="about-cards">
            <div
              v-for="metric in aboutMetrics"
              :key="metric.label"
              style="background:linear-gradient(135deg,#14532d,#166534);border-radius:16px;padding:28px;color:white;"
            >
              <i :class="metric.icon" style="font-size:22px;color:#fbbf24;display:block;margin-bottom:12px;"></i>
              <p style="font-size:2rem;font-weight:800;margin:0 0 4px;">{{ metric.value }}</p>
              <p style="font-size:13px;color:#a7f3d0;margin:0;">{{ metric.label }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

  </LandingLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Chart         from 'primevue/chart'
import LandingLayout from '@/components/layout/LandingLayout.vue'
import IndonesiaMap  from '@/components/charts/IndonesiaMap.vue'
import ReportService from '@/services/report'
import { formatRupiah }       from '@/utils/formatter'
import { useLoginModalStore } from '@/stores/loginModal'

const loginModal = useLoginModalStore()
const mapMetric  = ref('mustahik')
const mapData    = ref([])
const genderData = ref({ male_count: 0, female_count: 0 })
const bidangData = ref([])
const trendData  = ref([])
const summary    = ref({ total_penyaluran: 0, penerima_manfaat: 0, nasional: 0, provinsi: 0, kabkota: 0 })

const metricOptions = [
  { label: 'Jumlah Mustahik',  value: 'mustahik'   },
  { label: 'Total Penyaluran', value: 'penyaluran' },
]

onMounted(async () => {
  try {
    const [s, g, b, t, m] = await Promise.all([
      ReportService.getHomeSummary(),
      ReportService.getByGender({}),
      ReportService.getByBidang({}),
      ReportService.getTimeseries({}),
      ReportService.getMapData('1'),
    ])
    summary.value    = s
    genderData.value = g
    bidangData.value = b
    trendData.value  = t
    mapData.value    = Array.isArray(m) ? m : []
  } catch (e) {
    console.error('Failed to load landing data', e)
  }
})

const heroStats = computed(() => [
  { label: 'Total Penyaluran', value: formatRupiah(summary.value?.total_penyaluran||0), icon:'pi pi-wallet',     sub:'Seluruh LAZ terdaftar' },
  { label: 'LAZ Nasional',     value: summary.value?.nasional||0,                        icon:'pi pi-building',   sub:'Lembaga aktif' },
  { label: 'LAZ Provinsi',     value: summary.value?.provinsi||0,                        icon:'pi pi-map-marker', sub:'Lembaga aktif' },
  { label: 'Mustahik',         value: (summary.value?.penerima_manfaat||0).toLocaleString('id-ID'), icon:'pi pi-users', sub:'Penerima manfaat' },
])

const aggStats = computed(() => [
  { label:'Total Penyaluran',  value:formatRupiah(summary.value?.total_penyaluran||0), sub:'Akumulasi seluruh LAZ', icon:'pi pi-wallet',     iconBg:'#f0fdf4', iconColor:'#16a34a' },
  { label:'Penerima Manfaat',  value:(summary.value?.penerima_manfaat||0).toLocaleString('id-ID'), sub:'Total mustahik unik', icon:'pi pi-users', iconBg:'#eff6ff', iconColor:'#2563eb' },
  { label:'LAZ Terdaftar',     value:((summary.value?.nasional||0)+(summary.value?.provinsi||0)+(summary.value?.kabkota||0)).toLocaleString('id-ID'), sub:'Nasional + Provinsi + Kab/Kota', icon:'pi pi-building', iconBg:'#faf5ff', iconColor:'#7c3aed' },
  { label:'Provinsi Terlibat', value:'34', sub:'Seluruh Indonesia', icon:'pi pi-map', iconBg:'#fff7ed', iconColor:'#ea580c' },
])

const topProvinces = computed(() => {
  const sorted = [...mapData.value].sort((a,b)=>(b.mustahik||0)-(a.mustahik||0)).slice(0,5)
  const max    = sorted[0]?.mustahik||1
  return sorted.map(p=>({...p, pct:Math.round((p.mustahik/max)*100)}))
})

const topProvincesByPenyaluran = computed(() => {
  const sorted = [...mapData.value].sort((a,b)=>(b.penyaluran||0)-(a.penyaluran||0)).slice(0,5)
  const max    = sorted[0]?.penyaluran||1
  return sorted.map(p=>({...p, pct_penyaluran:Math.round((p.penyaluran/max)*100)}))
})

const bidangProgram = computed(() => {
  const total = bidangData.value.reduce((s,b)=>s+(b.total_penyaluran||0),0)||1
  return bidangData.value.map(b=>({...b, pct:((b.total_penyaluran||0)/total)*100}))
})

const genderChartData = computed(() => ({
  labels:['Laki-laki','Perempuan'],
  datasets:[{ data:[genderData.value?.male_count||0, genderData.value?.female_count||0], backgroundColor:['#3b82f6','#ec4899'], borderWidth:0 }]
}))
const bidangChartData = computed(() => ({
  labels: bidangData.value.map(d=>d.bidang_label),
  datasets:[{ data:bidangData.value.map(d=>d.total_penyaluran||0), backgroundColor:'rgba(22,163,74,0.7)', borderRadius:4 }]
}))
const trendChartData = computed(() => ({
  labels: trendData.value.map(d=>d.tahun),
  datasets:[{ label:'Penyaluran', data:trendData.value.map(d=>(d.Bantuan_Langsung||0)+(d.Bantuan_Tidak_Langsung||0)), borderColor:'#16a34a', backgroundColor:'rgba(22,163,74,0.1)', fill:true, tension:0.4, pointRadius:3 }]
}))

const doughnutOpts = { plugins:{ legend:{ position:'bottom', labels:{ font:{ size:11 } } } }, responsive:true, maintainAspectRatio:false }
const barOpts      = { indexAxis:'y', plugins:{ legend:{ display:false } }, responsive:true, maintainAspectRatio:false, scales:{ x:{ ticks:{ font:{ size:9 } } }, y:{ ticks:{ font:{ size:10 } } } } }
const lineOpts     = { plugins:{ legend:{ display:false } }, responsive:true, maintainAspectRatio:false, scales:{ y:{ ticks:{ font:{ size:9 } } } } }

const bidangColors = [
  { bg:'#f0fdf4', icon:'#16a34a' },
  { bg:'#eff6ff', icon:'#2563eb' },
  { bg:'#faf5ff', icon:'#7c3aed' },
  { bg:'#fff7ed', icon:'#ea580c' },
  { bg:'#fef2f2', icon:'#dc2626' },
  { bg:'#f0fdfa', icon:'#0d9488' },
]
const bidangIcons = ['pi pi-heart','pi pi-book','pi pi-briefcase','pi pi-home','pi pi-shield','pi pi-star']

const features = [
  { icon:'pi pi-shield',     title:'Data Terverifikasi',       desc:'Terintegrasi langsung dengan DTSEN.' },
  { icon:'pi pi-map',        title:'Pemetaan Wilayah',         desc:'Sebaran mustahik hingga tingkat kelurahan di seluruh Indonesia.' },
  { icon:'pi pi-chart-line', title:'Analitik Real-time',       desc:'Dashboard interaktif dengan filter multidimensi dan ekspor data.' },
  { icon:'pi pi-users',      title:'Profil Mustahik Lengkap',  desc:'Data sosiodemografi penerima termasuk desil kemiskinan.' },
]

const aboutMetrics = [
  { icon:'pi pi-database', label:'Sumber Data Terintegrasi', value:'5+' },
  { icon:'pi pi-clock',    label:'Pembaruan Data',           value:'Harian' },
  { icon:'pi pi-check',    label:'Akurasi Penargetan',       value:'94%' },
  { icon:'pi pi-map',      label:'Cakupan Wilayah',          value:'34 Prov' },
]

function scrollTo(id) {
  document.querySelector(id)?.scrollIntoView({ behavior:'smooth' })
}
</script>

<style scoped>
.hero-grid    { display:grid; grid-template-columns:1fr 1fr; gap:48px; align-items:center; }
.hero-cards   { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.grid-4       { grid-template-columns: repeat(4, 1fr); }
.grid-3       { grid-template-columns: repeat(3, 1fr); }
.grid-2       { grid-template-columns: 1fr 1fr; }
.tentang-grid { display:grid; grid-template-columns:1fr 1fr; gap:64px; align-items:start; }
.about-cards  { display:grid; grid-template-columns:1fr 1fr; gap:16px; }

@media (max-width: 1024px) {
  .grid-4       { grid-template-columns: repeat(2, 1fr); }
  .hero-grid    { grid-template-columns: 1fr; }
  .tentang-grid { grid-template-columns: 1fr; gap:40px; }
}
@media (max-width: 768px) {
  .grid-3      { grid-template-columns: 1fr; }
  .grid-2      { grid-template-columns: 1fr; }
  .hero-cards  { grid-template-columns: 1fr 1fr; }
  .about-cards { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 480px) {
  .hero-cards  { grid-template-columns: 1fr; }
}

@keyframes bounce {
  0%,100% { transform:translateX(-50%) translateY(0); }
  50%      { transform:translateX(-50%) translateY(6px); }
}
</style>
