<template>
  <LandingLayout>

    <!-- ======== HERO ======== -->
    <section
      id="hero"
      class="relative min-h-screen flex items-center bg-gradient-to-br from-primary-900 via-primary-800 to-primary-600 overflow-hidden pt-16"
    >
      <!-- Decorative blobs -->
      <div class="absolute top-0 right-0 w-96 h-96 bg-secondary/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
      <div class="absolute bottom-0 left-0 w-72 h-72 bg-primary-400/20 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2"></div>

      <div class="relative max-w-7xl mx-auto px-6 py-20 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <!-- Left: copy -->
        <div>
          <Tag value="Data Tunggal Sosial Ekonomi Nasional" severity="warning" class="mb-5" />
          <h1 class="text-4xl md:text-5xl xl:text-6xl font-extrabold text-white leading-tight mb-5">
            Sistem Informasi<br />
            <span class="text-secondary">Zakat & Wakaf</span><br />
            Nasional
          </h1>
          <p class="text-primary-200 text-lg leading-relaxed mb-8 max-w-lg">
            Platform pemantauan penyaluran zakat berbasis data desil kemiskinan Bappenas.
            Transparan, terukur, dan tepat sasaran.
          </p>
          <div class="flex flex-wrap gap-3">
            <Button
              label="Lihat Statistik"
              icon="pi pi-chart-bar"
              size="large"
              class="bg-secondary border-secondary hover:bg-secondary-dark text-white"
              @click="scrollTo('#stats')"
            />
            <Button
              label="Masuk Sistem"
              icon="pi pi-sign-in"
              size="large"
              outlined
              class="text-white border-white hover:bg-white/10"
              @click="$router.push('/login')"
            />
          </div>
        </div>

        <!-- Right: hero stats card -->
        <div class="grid grid-cols-2 gap-4">
          <div
            v-for="stat in heroStats"
            :key="stat.label"
            class="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-5 text-white"
          >
            <div class="flex items-center gap-2 mb-2">
              <i :class="[stat.icon, 'text-secondary text-xl']"></i>
              <span class="text-xs text-primary-300 font-medium uppercase tracking-wide">{{ stat.label }}</span>
            </div>
            <p class="text-3xl font-bold">{{ stat.value }}</p>
            <p class="text-xs text-primary-300 mt-1">{{ stat.sub }}</p>
          </div>
        </div>
      </div>

      <!-- Scroll indicator -->
      <div class="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 text-primary-300 animate-bounce">
        <span class="text-xs">Gulir ke bawah</span>
        <i class="pi pi-angle-down"></i>
      </div>
    </section>

    <!-- ======== AGGREGATE STATS ======== -->
    <section id="stats" class="py-20 bg-gray-50">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-12">
          <Tag value="Data Real-time" severity="success" class="mb-3" />
          <h2 class="text-3xl font-bold text-gray-800">Statistik Nasional</h2>
          <p class="text-gray-500 mt-2 max-w-lg mx-auto">Agregat penyaluran zakat seluruh LAZ terdaftar di Indonesia per hari ini.</p>
        </div>

        <!-- Stat cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-12">
          <div
            v-for="stat in aggStats"
            :key="stat.label"
            class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col gap-2 hover:shadow-md transition-shadow"
          >
            <div :class="['w-11 h-11 rounded-xl flex items-center justify-center', stat.iconBg]">
              <i :class="[stat.icon, 'text-xl', stat.iconColor]"></i>
            </div>
            <p class="text-2xl font-bold text-gray-800 mt-1">{{ stat.value }}</p>
            <p class="text-sm font-medium text-gray-600">{{ stat.label }}</p>
            <p class="text-xs text-gray-400">{{ stat.sub }}</p>
          </div>
        </div>

        <!-- Mini charts row -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <!-- Gender -->
          <Card class="shadow-sm border border-gray-100">
            <template #title><span class="text-sm font-semibold">Gender Penerima</span></template>
            <template #content>
              <Chart
                type="doughnut"
                :data="genderChartData"
                :options="{ plugins: { legend: { position: 'bottom' } }, responsive: true, maintainAspectRatio: false }"
                style="height: 180px"
              />
            </template>
          </Card>

          <!-- Bidang -->
          <Card class="shadow-sm border border-gray-100">
            <template #title><span class="text-sm font-semibold">Penyaluran per Bidang</span></template>
            <template #content>
              <Chart
                type="bar"
                :data="bidangChartData"
                :options="{ indexAxis: 'y', plugins: { legend: { display: false } }, responsive: true, maintainAspectRatio: false, scales: { x: { ticks: { font: { size: 9 } } }, y: { ticks: { font: { size: 9 } } } } }"
                style="height: 180px"
              />
            </template>
          </Card>

          <!-- Tren tahunan -->
          <Card class="shadow-sm border border-gray-100">
            <template #title><span class="text-sm font-semibold">Tren Penyaluran</span></template>
            <template #content>
              <Chart
                type="line"
                :data="trendChartData"
                :options="{ plugins: { legend: { display: false } }, responsive: true, maintainAspectRatio: false, scales: { y: { ticks: { font: { size: 9 } } } } }"
                style="height: 180px"
              />
            </template>
          </Card>
        </div>
      </div>
    </section>

    <!-- ======== PETA SEBARAN ======== -->
    <section id="map" class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-10">
          <Tag value="Sebaran Wilayah" severity="info" class="mb-3" />
          <h2 class="text-3xl font-bold text-gray-800">Peta Sebaran Mustahik</h2>
          <p class="text-gray-500 mt-2 max-w-lg mx-auto">Distribusi penerima manfaat zakat per provinsi di seluruh Indonesia.</p>
        </div>

        <!-- Metric toggle -->
        <div class="flex justify-center mb-6">
          <SelectButton
            v-model="mapMetric"
            :options="metricOptions"
            option-label="label"
            option-value="value"
          />
        </div>

        <IndonesiaMap
          :map-data="mapData"
          :metric="mapMetric"
          height="500px"
        />

        <!-- Province top 5 -->
        <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 class="font-semibold text-gray-700 mb-3">5 Provinsi Terbanyak Mustahik</h3>
            <div class="space-y-2">
              <div
                v-for="(prov, i) in topProvinces"
                :key="prov.provinsi_nama"
                class="flex items-center gap-3"
              >
                <span class="w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-bold flex items-center justify-center flex-shrink-0">{{ i+1 }}</span>
                <div class="flex-1">
                  <div class="flex justify-between text-sm mb-0.5">
                    <span class="font-medium text-gray-700">{{ prov.provinsi_nama }}</span>
                    <span class="text-gray-500">{{ prov.mustahik?.toLocaleString('id-ID') }}</span>
                  </div>
                  <ProgressBar :value="prov.pct" :show-value="false" style="height: 6px" />
                </div>
              </div>
            </div>
          </div>
          <div>
            <h3 class="font-semibold text-gray-700 mb-3">5 Provinsi Penyaluran Terbesar</h3>
            <div class="space-y-2">
              <div
                v-for="(prov, i) in topProvincesByPenyaluran"
                :key="prov.provinsi_nama"
                class="flex items-center gap-3"
              >
                <span class="w-6 h-6 rounded-full bg-secondary/20 text-secondary-dark text-xs font-bold flex items-center justify-center flex-shrink-0">{{ i+1 }}</span>
                <div class="flex-1">
                  <div class="flex justify-between text-sm mb-0.5">
                    <span class="font-medium text-gray-700">{{ prov.provinsi_nama }}</span>
                    <span class="text-gray-500">{{ formatRupiah(prov.penyaluran) }}</span>
                  </div>
                  <ProgressBar :value="prov.pct_penyaluran" :show-value="false" style="height: 6px" class="[&_.p-progressbar-value]:bg-secondary" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ======== PROGRAM / BIDANG ======== -->
    <section id="program" class="py-20 bg-gray-50">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-12">
          <Tag value="Kategori Penyaluran" severity="warning" class="mb-3" />
          <h2 class="text-3xl font-bold text-gray-800">Program Bidang Zakat</h2>
          <p class="text-gray-500 mt-2">Penyaluran berdasarkan kategori bidang program BAZNAS.</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <div
            v-for="(bidang, i) in bidangProgram"
            :key="bidang.bidang_label"
            class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
          >
            <div :class="['w-10 h-10 rounded-xl flex items-center justify-center mb-4', bidangColors[i % bidangColors.length].bg]">
              <i :class="[bidangIcons[i % bidangIcons.length], 'text-lg', bidangColors[i % bidangColors.length].icon]"></i>
            </div>
            <h3 class="font-semibold text-gray-800 mb-1">{{ bidang.bidang_label }}</h3>
            <p class="text-xl font-bold text-primary-600">{{ formatRupiah(bidang.total_penyaluran || 0) }}</p>
            <div class="mt-3">
              <div class="flex justify-between text-xs text-gray-400 mb-1">
                <span>Porsi dari total</span>
                <span>{{ bidang.pct?.toFixed(1) || 0 }}%</span>
              </div>
              <ProgressBar :value="bidang.pct || 0" :show-value="false" style="height: 4px" />
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ======== TENTANG ======== -->
    <section id="tentang" class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <Tag value="Tentang Sistem" severity="secondary" class="mb-4" />
            <h2 class="text-3xl font-bold text-gray-800 mb-4">Mengapa DTSEN?</h2>
            <p class="text-gray-500 leading-relaxed mb-6">
              DTSEN mengintegrasikan data penerima manfaat zakat dari seluruh LAZ terdaftar dengan data
              desil kemiskinan Bappenas, memastikan penyaluran zakat tepat sasaran kepada kelompok yang
              paling membutuhkan.
            </p>
            <div class="space-y-4">
              <div v-for="feat in features" :key="feat.title" class="flex gap-4">
                <div class="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center flex-shrink-0">
                  <i :class="[feat.icon, 'text-primary-600']"></i>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-800 text-sm">{{ feat.title }}</h4>
                  <p class="text-xs text-gray-500 mt-0.5">{{ feat.desc }}</p>
                </div>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div v-for="metric in aboutMetrics" :key="metric.label"
              class="bg-gradient-to-br from-primary-700 to-primary-600 rounded-2xl p-6 text-white"
            >
              <i :class="[metric.icon, 'text-2xl text-secondary mb-3 block']"></i>
              <p class="text-3xl font-bold">{{ metric.value }}</p>
              <p class="text-sm text-primary-200 mt-1">{{ metric.label }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

  </LandingLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Button       from 'primevue/button'
import Tag          from 'primevue/tag'
import Card         from 'primevue/card'
import Chart        from 'primevue/chart'
import SelectButton from 'primevue/selectbutton'
import ProgressBar  from 'primevue/progressbar'
import LandingLayout  from '@/components/layout/LandingLayout.vue'
import IndonesiaMap   from '@/components/charts/IndonesiaMap.vue'
import ReportService  from '@/services/report'
import { formatRupiah } from '@/utils/formatter'

// ---- Data ----
const mapMetric   = ref('mustahik')
const mapData     = ref([])
const genderData  = ref({ male_count: 0, female_count: 0 })
const bidangData  = ref([])
const trendData   = ref([])
const summary     = ref({ total_penyaluran: 0, penerima_manfaat: 0 })

const metricOptions = [
  { label: 'Jumlah Mustahik',  value: 'mustahik' },
  { label: 'Total Penyaluran', value: 'penyaluran' },
]

// ---- Lifecycle ----
onMounted(async () => {
  try {
    const [s, g, b, t, m] = await Promise.all([
      ReportService.getHomeSummary(),
      ReportService.getByGender({}),
      ReportService.getByBidang({}),
      ReportService.getTimeseries({}),
      ReportService.getMapData('1')
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

// ---- Computed ----
const heroStats = computed(() => [
  { label: 'Total Penyaluran', value: formatRupiah(summary.value?.total_penyaluran || 0), icon: 'pi pi-wallet',    sub: 'Seluruh LAZ terdaftar' },
  { label: 'LAZ Nasional',     value: summary.value?.nasional  || 0,                       icon: 'pi pi-building',  sub: 'Lembaga aktif' },
  { label: 'LAZ Provinsi',     value: summary.value?.provinsi  || 0,                       icon: 'pi pi-map-marker',sub: 'Lembaga aktif' },
  { label: 'Mustahik',         value: (summary.value?.penerima_manfaat || 0).toLocaleString('id-ID'), icon: 'pi pi-users', sub: 'Penerima manfaat' },
])

const aggStats = computed(() => [
  { label: 'Total Penyaluran',  value: formatRupiah(summary.value?.total_penyaluran || 0), sub: 'Akumulasi seluruh LAZ', icon: 'pi pi-wallet',     iconBg: 'bg-green-50',  iconColor: 'text-green-600' },
  { label: 'Penerima Manfaat',  value: (summary.value?.penerima_manfaat || 0).toLocaleString('id-ID'), sub: 'Total mustahik unik', icon: 'pi pi-users',      iconBg: 'bg-blue-50',   iconColor: 'text-blue-600' },
  { label: 'LAZ Terdaftar',     value: ((summary.value?.nasional||0)+(summary.value?.provinsi||0)+(summary.value?.kabkota||0)).toLocaleString('id-ID'), sub: 'Nasional + Provinsi + Kab/Kota', icon: 'pi pi-building',   iconBg: 'bg-purple-50', iconColor: 'text-purple-600' },
  { label: 'Provinsi Terlibat', value: '34',                                                sub: 'Seluruh Indonesia',      icon: 'pi pi-map',        iconBg: 'bg-orange-50', iconColor: 'text-orange-600' },
])

const topProvinces = computed(() => {
  const sorted = [...mapData.value].sort((a, b) => (b.mustahik || 0) - (a.mustahik || 0)).slice(0, 5)
  const max    = sorted[0]?.mustahik || 1
  return sorted.map(p => ({ ...p, pct: Math.round((p.mustahik / max) * 100) }))
})

const topProvincesByPenyaluran = computed(() => {
  const sorted = [...mapData.value].sort((a, b) => (b.penyaluran || 0) - (a.penyaluran || 0)).slice(0, 5)
  const max    = sorted[0]?.penyaluran || 1
  return sorted.map(p => ({ ...p, pct_penyaluran: Math.round((p.penyaluran / max) * 100) }))
})

const bidangProgram = computed(() => {
  const total = bidangData.value.reduce((s, b) => s + (b.total_penyaluran || 0), 0) || 1
  return bidangData.value.map(b => ({ ...b, pct: ((b.total_penyaluran || 0) / total) * 100 }))
})

// ---- Chart data ----
const genderChartData = computed(() => ({
  labels: ['Laki-laki', 'Perempuan'],
  datasets: [{ data: [genderData.value?.male_count || 0, genderData.value?.female_count || 0], backgroundColor: ['#3b82f6', '#f472b6'], borderWidth: 0 }]
}))

const bidangChartData = computed(() => ({
  labels: bidangData.value.map(d => d.bidang_label),
  datasets: [{ label: 'Penyaluran', data: bidangData.value.map(d => d.total_penyaluran || 0), backgroundColor: '#1a7f4f99' }]
}))

const trendChartData = computed(() => ({
  labels: trendData.value.map(d => d.tahun),
  datasets: [{ label: 'Penyaluran', data: trendData.value.map(d => (d.Bantuan_Langsung || 0) + (d.Bantuan_Tidak_Langsung || 0)), borderColor: '#1a7f4f', backgroundColor: '#1a7f4f22', fill: true, tension: 0.4 }]
}))

// ---- Static content ----
const bidangColors = [
  { bg: 'bg-green-50',  icon: 'text-green-600' },
  { bg: 'bg-blue-50',   icon: 'text-blue-600' },
  { bg: 'bg-purple-50', icon: 'text-purple-600' },
  { bg: 'bg-orange-50', icon: 'text-orange-600' },
  { bg: 'bg-red-50',    icon: 'text-red-600' },
  { bg: 'bg-teal-50',   icon: 'text-teal-600' },
]
const bidangIcons = ['pi pi-heart', 'pi pi-book', 'pi pi-briefcase', 'pi pi-home', 'pi pi-shield', 'pi pi-star']

const features = [
  { icon: 'pi pi-shield',    title: 'Data Terverifikasi',       desc: 'Terintegrasi langsung dengan DTSEN Bappenas dan SIMBA BAZNAS.' },
  { icon: 'pi pi-map',       title: 'Pemetaan Wilayah',         desc: 'Sebaran mustahik hingga tingkat kelurahan di seluruh Indonesia.' },
  { icon: 'pi pi-chart-line',title: 'Analitik Real-time',       desc: 'Dashboard interaktif dengan filter multidimensi dan ekspor data.' },
  { icon: 'pi pi-users',     title: 'Profil Mustahik Lengkap',  desc: 'Data sosiodemografi penerima termasuk desil kemiskinan.' },
]

const aboutMetrics = [
  { icon: 'pi pi-database', label: 'Sumber Data Terintegrasi', value: '5+' },
  { icon: 'pi pi-clock',    label: 'Pembaruan Data',           value: 'Harian' },
  { icon: 'pi pi-check',    label: 'Akurasi Penargetan',       value: '94%' },
  { icon: 'pi pi-map',      label: 'Cakupan Wilayah',          value: '34 Prov' },
]

function scrollTo(id) {
  document.querySelector(id)?.scrollIntoView({ behavior: 'smooth' })
}
</script>
