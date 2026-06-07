<template>
  <AppLayout>
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-2xl font-bold text-gray-800">Data Mustahik</h2>
        <Button icon="pi pi-download" label="Export" outlined size="small" />
      </div>

      <!-- Filter Panel -->
      <FilterPanel @apply="fetchData" @reset="onReset" :collapsed="true">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium">Nama</label>
            <InputText v-model="filters.nama" placeholder="Cari nama..." size="small" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium">Jenis Kelamin</label>
            <Select
              v-model="filters.jenis_kelamin"
              :options="genderOptions"
              option-label="label"
              option-value="value"
              placeholder="Semua"
              show-clear
              size="small"
            />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium">Agama</label>
            <Select
              v-model="filters.agama"
              :options="AGAMA_LIST"
              placeholder="Semua"
              show-clear
              size="small"
            />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium">Tipe Penerimaan</label>
            <Select
              v-model="filters.tipe_program"
              :options="tipeOptions"
              option-label="label"
              option-value="value"
              placeholder="Semua"
              show-clear
              size="small"
            />
          </div>
        </div>
      </FilterPanel>

      <!-- Table -->
      <Card class="shadow-sm">
        <template #content>
          <DtTable
            :data="tableData"
            :loading="loading"
            :total="total"
            :rows="perPage"
            @page="onPage"
          >
            <Column field="nama_pm" header="Nama Lengkap" sortable>
              <template #body="{ data }">
                <router-link
                  :to="`/mustahik/${data.nik_hashed}`"
                  class="text-primary-600 font-medium hover:underline"
                >
                  {{ data.nama_pm }}
                </router-link>
              </template>
            </Column>
            <Column field="jenis_kelamin" header="Gender">
              <template #body="{ data }">
                <Tag
                  :value="formatGender(data.jenis_kelamin)"
                  :severity="data.jenis_kelamin === 'm' ? 'info' : 'contrast'"
                />
              </template>
            </Column>
            <Column field="domisili" header="Domisili" />
            <Column field="nominal" header="Total Penyaluran">
              <template #body="{ data }">
                <span class="font-semibold text-green-700">{{ formatRupiah(data.nominal) }}</span>
              </template>
            </Column>
            <Column field="desil" header="Desil">
              <template #body="{ data }">
                <Badge :value="data.desil" :severity="desilSeverity(data.desil)" />
              </template>
            </Column>
            <Column header="Aksi" style="width: 80px">
              <template #body="{ data }">
                <Button
                  icon="pi pi-eye"
                  text
                  rounded
                  size="small"
                  v-tooltip="'Lihat Detail'"
                  @click="$router.push(`/mustahik/${data.nik_hashed}`)"
                />
              </template>
            </Column>
          </DtTable>
        </template>
      </Card>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import Button    from 'primevue/button'
import Card      from 'primevue/card'
import Column    from 'primevue/column'
import Tag       from 'primevue/tag'
import Badge     from 'primevue/badge'
import InputText  from 'primevue/inputtext'
import Select     from 'primevue/select'
import AppLayout  from '@/components/layout/AppLayout.vue'
import FilterPanel from '@/components/common/FilterPanel.vue'
import DtTable    from '@/components/common/DataTable.vue'
import MustahikService from '@/services/mustahik'
import { formatRupiah, formatGender } from '@/utils/formatter'
import { AGAMA_LIST, TIPE_PENERIMAAN } from '@/utils/constants'

const tableData = ref([])
const loading   = ref(false)
const total     = ref(0)
const page      = ref(1)
const perPage   = ref(20)

const filters = reactive({
  nama: null, jenis_kelamin: null, agama: null, tipe_program: null
})

const genderOptions = [
  { label: 'Laki-laki', value: 'm' },
  { label: 'Perempuan', value: 'f' }
]
const tipeOptions = Object.entries(TIPE_PENERIMAAN).map(([value, label]) => ({ label, value }))

const desilSeverity = (d) => {
  if (d <= 2) return 'danger'
  if (d <= 5) return 'warning'
  return 'success'
}

async function fetchData() {
  loading.value = true
  try {
    const active = Object.fromEntries(Object.entries(filters).filter(([, v]) => v))
    const res = await MustahikService.getList({ ...active, page: page.value, per_page: perPage.value })
    tableData.value = res.data || []
    total.value     = res.meta?.total || 0
  } finally {
    loading.value = false
  }
}

function onPage(e) {
  page.value = e.page + 1
  fetchData()
}

function onReset() {
  Object.keys(filters).forEach(k => (filters[k] = null))
  fetchData()
}

onMounted(fetchData)
</script>
