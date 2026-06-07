<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold text-gray-800">Dashboard</h2>
          <p class="text-sm text-gray-500 mt-0.5">Ringkasan data penyaluran zakat nasional</p>
        </div>
        <Button icon="pi pi-refresh" label="Perbarui" outlined size="small" :loading="loading" @click="loadData" />
      </div>

      <!-- Stat Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Penyaluran"
          :value="summary?.total_penyaluran || 0"
          icon="pi pi-wallet"
          icon-bg="bg-green-100"
          icon-color="text-green-600"
          format="currency"
        />
        <StatCard
          label="LAZ Nasional"
          :value="summary?.nasional || 0"
          icon="pi pi-building"
          icon-bg="bg-blue-100"
          icon-color="text-blue-600"
        />
        <StatCard
          label="LAZ Provinsi"
          :value="summary?.provinsi || 0"
          icon="pi pi-map-marker"
          icon-bg="bg-purple-100"
          icon-color="text-purple-600"
        />
        <StatCard
          label="LAZ Kab/Kota"
          :value="summary?.kabkota || 0"
          icon="pi pi-flag"
          icon-bg="bg-orange-100"
          icon-color="text-orange-600"
        />
      </div>

      <!-- Charts row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- Gender Chart -->
        <Card class="shadow-sm">
          <template #title>Penerima berdasarkan Gender</template>
          <template #content>
            <Chart type="pie" :data="genderChartData" :options="pieOptions" style="height: 260px" />
          </template>
        </Card>

        <!-- Timeseries Chart -->
        <Card class="shadow-sm">
          <template #title>Tren Penyaluran Tahunan</template>
          <template #content>
            <Chart type="bar" :data="timeseriesChartData" :options="barOptions" style="height: 260px" />
          </template>
        </Card>
      </div>

      <!-- Bidang breakdown -->
      <Card class="shadow-sm">
        <template #title>Penyaluran per Bidang Program</template>
        <template #content>
          <Chart type="bar" :data="bidangChartData" :options="horizontalBarOptions" style="height: 300px" />
        </template>
      </Card>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Button  from 'primevue/button'
import Card    from 'primevue/card'
import Chart   from 'primevue/chart'
import AppLayout from '@/components/layout/AppLayout.vue'
import StatCard  from '@/components/common/StatCard.vue'
import ReportService from '@/services/report'
import { formatRupiah } from '@/utils/formatter'

const loading       = ref(false)
const summary       = ref(null)
const genderData    = ref(null)
const bidangData    = ref([])
const timeseriesData = ref([])

async function loadData() {
  loading.value = true
  try {
    const [s, g, b, t] = await Promise.all([
      ReportService.getHomeSummary(),
      ReportService.getByGender({}),
      ReportService.getByBidang({}),
      ReportService.getTimeseries({})
    ])
    summary.value       = s
    genderData.value    = g
    bidangData.value    = b
    timeseriesData.value = t
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

// --- Chart configs ---
const genderChartData = computed(() => ({
  labels: ['Laki-laki', 'Perempuan'],
  datasets: [{
    data: [genderData.value?.male_count || 0, genderData.value?.female_count || 0],
    backgroundColor: ['#3b82f6', '#f472b6'],
    borderWidth: 0
  }]
}))

const timeseriesChartData = computed(() => ({
  labels: timeseriesData.value.map(d => d.tahun),
  datasets: [
    {
      label: 'Bantuan Langsung',
      data: timeseriesData.value.map(d => d.Bantuan_Langsung),
      backgroundColor: '#1a7f4f'
    },
    {
      label: 'Bantuan Tidak Langsung',
      data: timeseriesData.value.map(d => d.Bantuan_Tidak_Langsung),
      backgroundColor: '#f5a623'
    }
  ]
}))

const bidangChartData = computed(() => ({
  labels: bidangData.value.map(d => d.bidang_label),
  datasets: [{
    label: 'Total Penyaluran (Rp)',
    data: bidangData.value.map(d => d.total_penyaluran),
    backgroundColor: '#1a7f4f88'
  }]
}))

const pieOptions = {
  plugins: { legend: { position: 'bottom' } },
  responsive: true, maintainAspectRatio: false
}
const barOptions = {
  plugins: { legend: { position: 'bottom' } },
  responsive: true, maintainAspectRatio: false,
  scales: { y: { ticks: { callback: v => formatRupiah(v) } } }
}
const horizontalBarOptions = {
  indexAxis: 'y',
  plugins: { legend: { display: false } },
  responsive: true, maintainAspectRatio: false,
  scales: { x: { ticks: { callback: v => formatRupiah(v) } } }
}
</script>
