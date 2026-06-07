<template>
  <AppLayout>
    <div style="display:flex;flex-direction:column;gap:20px;">

      <!-- Top bar -->
      <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
        <Button icon="pi pi-arrow-left" label="Kembali" text size="small" @click="$router.back()" />
        <div style="flex:1;"></div>
        <!-- Filter bar -->
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
          <Select
            v-model="filterLaz"
            :options="lazOptions"
            option-label="label"
            option-value="value"
            placeholder="Filter LAZ"
            show-clear
            size="small"
            style="min-width:180px;"
            @change="applyFilter"
          />
          <Select
            v-model="filterProvinsi"
            :options="provinsiOptions"
            option-label="label"
            option-value="value"
            placeholder="Filter Provinsi"
            show-clear
            size="small"
            style="min-width:180px;"
            @change="applyFilter"
          />
          <Select
            v-model="filterBidang"
            :options="bidangOptions"
            option-label="label"
            option-value="value"
            placeholder="Filter Bidang"
            show-clear
            size="small"
            style="min-width:160px;"
            @change="applyFilter"
          />
          <Button
            icon="pi pi-filter-slash"
            label="Reset"
            outlined
            size="small"
            severity="secondary"
            @click="resetFilter"
          />
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" style="display:flex;justify-content:center;padding:64px 0;">
        <ProgressSpinner />
      </div>

      <!-- No data -->
      <div v-else-if="!filteredData.length" style="text-align:center;padding:64px 0;color:#94a3b8;">
        <i class="pi pi-inbox" style="font-size:3rem;display:block;margin-bottom:12px;"></i>
        <p style="font-size:14px;">Data tidak ditemukan.</p>
      </div>

      <!-- Cards -->
      <div v-else style="display:flex;flex-direction:column;gap:16px;">

        <!-- Summary bar -->
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:14px;padding:16px 20px;display:flex;gap:24px;flex-wrap:wrap;">
          <div>
            <p style="font-size:11px;color:#6b7280;font-weight:600;text-transform:uppercase;margin:0 0 2px;">Total Penyaluran</p>
            <p style="font-size:1.25rem;font-weight:800;color:#15803d;margin:0;">{{ formatRupiah(totalPenyaluran) }}</p>
          </div>
          <div>
            <p style="font-size:11px;color:#6b7280;font-weight:600;text-transform:uppercase;margin:0 0 2px;">Jumlah Program</p>
            <p style="font-size:1.25rem;font-weight:800;color:#1e293b;margin:0;">{{ filteredData.length }}</p>
          </div>
          <div>
            <p style="font-size:11px;color:#6b7280;font-weight:600;text-transform:uppercase;margin:0 0 2px;">Nama</p>
            <p style="font-size:1.25rem;font-weight:800;color:#1e293b;margin:0;">{{ filteredData[0]?.nama_lengkap || '—' }}</p>
          </div>
        </div>

        <!-- Detail cards -->
        <div
          v-for="(item, idx) in filteredData"
          :key="idx"
          style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:24px;box-shadow:0 1px 4px rgba(0,0,0,0.05);"
        >
          <!-- Card header -->
          <div style="display:flex;align-items:center;gap:14px;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid #f1f5f9;">
            <div style="width:48px;height:48px;border-radius:14px;background:#f0fdf4;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:800;color:#15803d;flex-shrink:0;">
              {{ (item.nama_lengkap || '?')[0].toUpperCase() }}
            </div>
            <div style="flex:1;min-width:0;">
              <p style="font-size:15px;font-weight:800;color:#1e293b;margin:0 0 2px;">{{ item.nama_lengkap || '—' }}</p>
              <p style="font-size:12px;color:#64748b;margin:0;">{{ item.laz_nama }} &bull; {{ item.skala }}</p>
            </div>
            <div style="text-align:right;flex-shrink:0;">
              <p style="font-size:11px;color:#94a3b8;margin:0 0 2px;">Total Penyaluran</p>
              <p style="font-size:1.1rem;font-weight:800;color:#16a34a;margin:0;">{{ formatRupiah(item.rupiah) }}</p>
            </div>
          </div>

          <!-- Fields grid -->
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;" class="detail-grid">
            <div v-for="field in fields(item)" :key="field.label">
              <p style="font-size:10px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;margin:0 0 3px;">{{ field.label }}</p>
              <p style="font-size:13px;font-weight:600;color:#374151;margin:0;word-break:break-word;">{{ field.value || '—' }}</p>
            </div>
          </div>

          <!-- Desil badge -->
          <div style="margin-top:16px;padding-top:14px;border-top:1px solid #f1f5f9;display:flex;align-items:center;gap:10px;">
            <span style="font-size:12px;color:#64748b;">Desil Kemiskinan:</span>
            <span
              :style="desilStyle(item.desil)"
              style="padding:3px 12px;border-radius:99px;font-size:12px;font-weight:700;"
            >Desil {{ item.desil || '—' }}</span>
            <span style="font-size:12px;color:#64748b;">Bidang: <strong>{{ item.bidang_label || '—' }}</strong></span>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Button         from 'primevue/button'
import Select         from 'primevue/select'
import ProgressSpinner from 'primevue/progressspinner'
import AppLayout from '@/components/layout/AppLayout.vue'
import MustahikService from '@/services/mustahik'
import { formatRupiah, formatDate, formatGender } from '@/utils/formatter'

const route   = useRoute()
const detail  = ref([])
const loading = ref(false)

const filterLaz      = ref(null)
const filterProvinsi = ref(null)
const filterBidang   = ref(null)

onMounted(async () => {
  loading.value = true
  try {
    const res  = await MustahikService.getDetail(route.params.nikHashed)
    detail.value = res?.data || []
  } finally {
    loading.value = false
  }
})

// Build filter options from loaded data
const lazOptions = computed(() => {
  const unique = [...new Set(detail.value.map(d=>d.laz_nama).filter(Boolean))]
  return unique.map(v=>({ label:v, value:v }))
})
const provinsiOptions = computed(() => {
  const unique = [...new Set(detail.value.map(d=>d.provinsi_nama).filter(Boolean))]
  return unique.map(v=>({ label:v, value:v }))
})
const bidangOptions = computed(() => {
  const unique = [...new Set(detail.value.map(d=>d.bidang_label).filter(Boolean))]
  return unique.map(v=>({ label:v, value:v }))
})

const filteredData = computed(() => {
  return detail.value.filter(d => {
    if (filterLaz.value      && d.laz_nama      !== filterLaz.value)      return false
    if (filterProvinsi.value && d.provinsi_nama !== filterProvinsi.value) return false
    if (filterBidang.value   && d.bidang_label  !== filterBidang.value)   return false
    return true
  })
})

const totalPenyaluran = computed(() =>
  filteredData.value.reduce((sum, d) => sum + (d.rupiah || 0), 0)
)

function applyFilter() {} // reactivity handles it
function resetFilter() {
  filterLaz.value      = null
  filterProvinsi.value = null
  filterBidang.value   = null
}

const fields = (item) => [
  { label:'NIK',             value: item.nik },
  { label:'Jenis Kelamin',   value: formatGender(item.jenis_kelamin) },
  { label:'Tanggal Lahir',   value: formatDate(item.lahir_tanggal) },
  { label:'Agama',           value: item.agama },
  { label:'No. KK',          value: item.kk },
  { label:'Program',         value: item.program_nama },
  { label:'Skala LAZ',       value: item.skala },
  { label:'Provinsi',        value: item.provinsi_nama },
  { label:'Kab/Kota',        value: item.kabkota_nama },
  { label:'Kecamatan',       value: item.kecamatan_nama },
  { label:'Kelurahan',       value: item.kelurahan_nama },
  { label:'Alamat Domisili', value: item.alamat_domisili },
  { label:'Alamat KTP',      value: item.ktp_alamat },
]

const desilStyle = (d) => {
  if (!d) return { background:'#f1f5f9', color:'#94a3b8' }
  if (d <= 2) return { background:'#fee2e2', color:'#dc2626' }
  if (d <= 5) return { background:'#fef9c3', color:'#b45309' }
  return { background:'#dcfce7', color:'#15803d' }
}
</script>

<style scoped>
.detail-grid { grid-template-columns: repeat(3,1fr); }
@media (max-width:768px)  { .detail-grid { grid-template-columns: repeat(2,1fr); } }
@media (max-width:480px)  { .detail-grid { grid-template-columns: 1fr; } }
</style>
