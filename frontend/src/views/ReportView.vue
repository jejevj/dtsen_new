<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <h2 class="text-2xl font-bold text-gray-800">Laporan Analitik</h2>
        <Button icon="pi pi-sliders-h" label="Filter" outlined size="small" @click="filterVisible = true" />
      </div>

      <!-- Filter Drawer -->
      <Drawer v-model:visible="filterVisible" header="Filter Laporan" position="right" style="width: 380px">
        <div class="space-y-4">
          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium">Provinsi Domisili</label>
            <Select v-model="filters.provinsi_domisili" :options="[]" placeholder="Semua" show-clear size="small" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium">Rentang Waktu</label>
            <DatePicker v-model="dateRange" selection-mode="range" :manual-input="false" placeholder="Pilih rentang" size="small" class="w-full" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium">Skala LAZ</label>
            <SelectButton v-model="filters.skala" :options="skalaOptions" option-label="label" option-value="value" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium">Desil Kemiskinan</label>
            <div class="flex flex-wrap gap-2">
              <ToggleButton
                v-for="d in 11" :key="d-1"
                v-model="desilSelected[d-1]"
                :on-label="String(d-1)"
                :off-label="String(d-1)"
                class="w-10 h-9 text-xs"
              />
            </div>
          </div>
        </div>
        <template #footer>
          <div class="flex gap-2">
            <Button label="Reset"    outlined severity="secondary" class="flex-1" @click="resetFilters" />
            <Button label="Terapkan" class="flex-1" @click="applyFilters" />
          </div>
        </template>
      </Drawer>

      <!-- Summary row -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard label="Total Penerima"    :value="summary?.penerima_manfaat || 0" icon="pi pi-users"    icon-bg="bg-blue-100"   icon-color="text-blue-600" />
        <StatCard label="Total Penyaluran"  :value="summary?.penyaluran || 0"        icon="pi pi-wallet"   icon-bg="bg-green-100"  icon-color="text-green-600" format="currency" />
        <StatCard label="Program Aktif"     :value="bidangData.length"               icon="pi pi-list"     icon-bg="bg-purple-100" icon-color="text-purple-600" />
      </div>

      <!-- Charts 2x2 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card class="shadow-sm">
          <template #title>Gender</template>
          <template #content>
            <Chart type="doughnut" :data="genderChart" :options="pieOptions" style="height: 240px" />
          </template>
        </Card>
        <Card class="shadow-sm">
          <template #title>Penyaluran Langsung vs Tidak Langsung</template>
          <template #content>
            <Chart type="bar" :data="programChart" :options="barOptions" style="height: 240px" />
          </template>
        </Card>
        <Card class="shadow-sm">
          <template #title>Tren Tahunan</template>
          <template #content>
            <Chart type="line" :data="timeseriesChart" :options="lineOptions" style="height: 240px" />
          </template>
        </Card>
        <Card class="shadow-sm">
          <template #title>Distribusi Desil Kemiskinan</template>
          <template #content>
            <Chart type="bar" :data="desilChart" :options="desilOptions" style="height: 240px" />
          </template>
        </Card>
      </div>

      <!-- Bidang breakdown -->
      <Card class="shadow-sm">
        <template #title>Penyaluran per Bidang</template>
        <template #content>
          <Chart type="bar" :data="bidangChart" :options="hBarOptions" style="height: 300px" />
        </template>
      </Card>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import Button       from 'primevue/button'
import Card         from 'primevue/card'
import Chart        from 'primevue/chart'
import Drawer       from 'primevue/drawer'
import Select       from 'primevue/select'
import SelectButton from 'primevue/selectbutton'
import ToggleButton from 'primevue/togglebutton'
import DatePicker   from 'primevue/datepicker'
import AppLayout  from '@/components/layout/AppLayout.vue'
import StatCard   from '@/components/common/StatCard.vue'
import ReportService from '@/services/report'
import { formatRupiah } from '@/utils/formatter'

const filterVisible = ref(false)
const dateRange     = ref(null)
const desilSelected = reactive(Array(11).fill(false))
const filters       = reactive({ provinsi_domisili: null, skala: null })

const summary       = ref(null)
const genderData    = ref(null)
const programData   = ref(null)
const timeseriesData = ref([])
const desilData     = ref({})
const bidangData    = ref([])

const skalaOptions = [
  { label: 'Semua',    value: null },
  { label: 'Nasional', value: 1 },
  { label: 'Provinsi', value: 2 },
  { label: 'Kab/Kota', value: 3 }
]

async function fetchAll(params = {}) {
  const [s, g, p, t, d, b] = await Promise.all([
    ReportService.getSummary(params),
    ReportService.getByGender(params),
    ReportService.getPenyaluranByProgram ? ReportService.getPenyaluranByProgram(params) : Promise.resolve(null),
    ReportService.getTimeseries(params),
    ReportService.getDesilSummary(params),
    ReportService.getByBidang(params)
  ])
  summary.value        = s
  genderData.value     = g
  programData.value    = p
  timeseriesData.value = t
  desilData.value      = d
  bidangData.value     = b
}

function buildParams() {
  const p = { ...filters }
  if (dateRange.value?.[0]) p.waktu_start = dateRange.value[0].toISOString().split('T')[0]
  if (dateRange.value?.[1]) p.waktu_end   = dateRange.value[1].toISOString().split('T')[0]
  desilSelected.forEach((v, i) => { if (v) p[`desil${i}`] = 1 })
  return p
}

function applyFilters() { filterVisible.value = false; fetchAll(buildParams()) }
function resetFilters() {
  Object.keys(filters).forEach(k => (filters[k] = null))
  desilSelected.fill(false)
  dateRange.value = null
  fetchAll()
}

onMounted(fetchAll)

// Chart data
const genderChart = computed(() => ({
  labels: ['Laki-laki', 'Perempuan'],
  datasets: [{ data: [genderData.value?.male_count || 0, genderData.value?.female_count || 0], backgroundColor: ['#3b82f6','#f472b6'], borderWidth: 0 }]
}))
const programChart = computed(() => ({
  labels: ['Langsung', 'Tidak Langsung'],
  datasets: [{ data: [programData.value?.langsung_total || 0, programData.value?.tidak_langsung_total || 0], backgroundColor: ['#1a7f4f','#f5a623'] }]
}))
const timeseriesChart = computed(() => ({
  labels: timeseriesData.value.map(d => d.tahun),
  datasets: [
    { label: 'Langsung',        data: timeseriesData.value.map(d => d.Bantuan_Langsung),        borderColor: '#1a7f4f', tension: 0.4, fill: false },
    { label: 'Tidak Langsung',  data: timeseriesData.value.map(d => d.Bantuan_Tidak_Langsung),  borderColor: '#f5a623', tension: 0.4, fill: false }
  ]
}))
const desilChart = computed(() => ({
  labels: Array.from({length:11}, (_,i) => `Desil ${i}`),
  datasets: [{ label: 'Jumlah Mustahik', data: Array.from({length:11}, (_,i) => desilData.value[i] || 0), backgroundColor: '#6366f1' }]
}))
const bidangChart = computed(() => ({
  labels: bidangData.value.map(d => d.bidang_label),
  datasets: [{ label: 'Total (Rp)', data: bidangData.value.map(d => d.total_penyaluran), backgroundColor: '#1a7f4f88' }]
}))

const pieOptions  = { plugins: { legend: { position: 'bottom' } }, responsive: true, maintainAspectRatio: false }
const barOptions  = { plugins: { legend: { display: false } }, responsive: true, maintainAspectRatio: false }
const lineOptions = { plugins: { legend: { position: 'bottom' } }, responsive: true, maintainAspectRatio: false }
const desilOptions = { plugins: { legend: { display: false } }, responsive: true, maintainAspectRatio: false }
const hBarOptions = { indexAxis: 'y', plugins: { legend: { display: false } }, responsive: true, maintainAspectRatio: false }
</script>
