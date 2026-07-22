<template>
  <AppLayout>
    <div class="space-y-5">
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 class="text-xl font-bold text-slate-800">Data Penerima Manfaat</h2>
          <p class="text-sm text-slate-500 mt-0.5">Daftar penerima manfaat zakat</p>
        </div>
        <Button
          icon="pi pi-filter"
          label="Filter"
          severity="primary"
          outlined
          size="small"
          @click="showFilter = true"
        >
          <template #default>
            <span>Filter</span>
            <span
              v-if="activeFilterCount > 0"
              class="ml-1.5 inline-flex items-center justify-center w-4 h-4 rounded-full bg-primary-600 text-white text-[10px] font-bold"
            >{{ activeFilterCount }}</span>
          </template>
        </Button>
      </div>
      <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        <div class="flex items-center justify-between gap-3 px-5 py-3 border-b border-slate-100">
          <div class="flex items-center gap-2">
            <i class="pi pi-users text-slate-400"></i>
            <span class="text-sm font-semibold text-slate-700">Daftar Mustahik</span>
            <span
              v-if="activeFilterCount > 0"
              class="ml-1 px-2 py-0.5 bg-primary-50 text-primary-700 border border-primary-200 text-xs font-semibold rounded-full"
            >{{ activeFilterCount }} filter aktif</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-400">Cari:</span>
            <InputText
              v-model="globalSearch"
              placeholder="Nama / NIK"
              class="text-sm"
              style="width:200px"
              @keyup.enter="applyFilter"
            />
          </div>
        </div>
        <div v-if="tableLoading" class="flex justify-center items-center py-16 text-slate-400">
          <i class="pi pi-spin pi-spinner mr-2"></i> Memuat data…
        </div>
        <div v-else-if="tableError" class="py-12 text-center text-red-500 text-sm">
          <i class="pi pi-exclamation-circle text-2xl mb-2 block"></i>
          {{ tableError }}
        </div>
        <div v-else-if="rows.length === 0" class="py-16 text-center text-slate-400 text-sm">
          <i class="pi pi-inbox text-3xl mb-3 block opacity-30"></i>
          Tidak ada data penerima manfaat yang sesuai filter.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <tr>
                <th class="px-5 py-3 text-left">No</th>
                <th class="px-5 py-3 text-left">Nama Lengkap</th>
                <th class="px-5 py-3 text-left">NIK</th>
                <th class="px-5 py-3 text-left">Jenis Kelamin</th>
                <th class="px-5 py-3 text-left">Provinsi</th>
                <th class="px-5 py-3 text-left">Kab/Kota</th>
                <th class="px-5 py-3 text-left">Usia</th>
                <th class="px-5 py-3 text-left">Desil</th>
                <th class="px-5 py-3 text-left">Jumlah Lembaga Pemberi</th>
                <th class="px-5 py-3 text-left">Jumlah Penerimaan</th>
                <th class="px-5 py-3 text-left">Total Nominal Penerimaan</th>
                <th class="px-5 py-3 text-left">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="(row, i) in rows" :key="row.mustahik_id ?? i"
                class="hover:bg-slate-50 transition-colors">
                <td class="px-5 py-3 text-slate-400">{{ (pagination.page - 1) * pagination.perPage + i + 1 }}</td>
                <td class="px-5 py-3 font-medium text-slate-800">{{ row.nama_lengkap ?? '-' }}</td>
                <td class="px-5 py-3 text-slate-600 font-mono text-xs">{{ row.nik ?? '-' }}</td>
                <td class="px-5 py-3">
                  <span :class="row.jenis_kelamin === 'm' ? 'bg-blue-50 text-blue-700' : 'bg-pink-50 text-pink-700'"
                    class="px-2 py-0.5 rounded-full text-xs font-semibold" >
                    {{ row.jenis_kelamin === 'm' ? 'Laki-laki' : 'Perempuan' }}
                  </span>
                </td>
                <td class="px-5 py-3 text-slate-600">{{ row.provinsi_nama ?? '-' }}</td>
                <td class="px-5 py-3 text-slate-600">{{ row.kabkota_nama ?? '-' }}</td>
                
                <td class="px-5 py-3">{{ row.usia ?? '-' }} Tahun</td>
                <td class="px-5 py-3">
                  {{ row.desil > 0 ? row.desil : 'N/A' }}
                </td>
                <td class="px-5 py-3 text-slate-600">{{ row.total_laz_kontribusi ?? '-' }} Lembaga</td>
                <td class="px-5 py-3 text-slate-600">{{ row.total_transaksi ?? '-' }} Kali</td>
                <td class="px-5 py-3 text-slate-600">{{ formatRupiah(row.total_rupiah) }}</td>
                <td class="px-5 py-3">
                  <Button
                    label="Detail"
                    icon="pi pi-eye"
                    iconPos="right"
                    text
                    rounded
                    size="small"
                    class="text-primary-600"
                    @click="$router.push('/mustahik/' + row.nik_hashed)"
                    v-tooltip="'Lihat Detail'"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="rows.length > 0" class="flex items-center justify-between px-5 py-3 border-t border-slate-100">
          <span class="text-xs text-slate-400">
            Halaman {{ pagination.page }} dari {{ pagination.totalPages }}
            · Total {{ pagination.total.toLocaleString('id-ID') }} data
          </span>
          <div class="flex gap-1">
            <Button icon="pi pi-angle-left" text rounded size="small" :disabled="pagination.page <= 1" @click="changePage(pagination.page - 1)" />
            <Button icon="pi pi-angle-right" text rounded size="small" :disabled="pagination.page >= pagination.totalPages" @click="changePage(pagination.page + 1)" />
          </div>
        </div>
      </div>
    </div>
    <teleport to="body">
      <transition name="fade-backdrop">
        <div
          v-if="showFilter"
          class="fixed inset-0 bg-black/30 z-40"
          @click="showFilter = false"
        />
      </transition>
      <transition name="slide-right">
        <div
          v-if="showFilter"
          class="fixed top-0 right-0 h-full w-full max-w-md bg-white shadow-2xl z-50 flex flex-col"
        >
          <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100">
            <div class="flex items-center gap-2">
              <i class="pi pi-filter text-primary-600"></i>
              <span class="font-semibold text-slate-800">Filter Pencarian</span>
              <span
                v-if="activeFilterCount > 0"
                class="px-2 py-0.5 bg-primary-600 text-white text-xs font-bold rounded-full"
              >{{ activeFilterCount }}</span>
            </div>
            <button
              class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100 text-slate-500 transition"
              @click="showFilter = false"
            >
              <i class="pi pi-times text-sm"></i>
            </button>
          </div>
          <div class="flex-1 overflow-y-auto px-5 py-4 space-y-5">
            <div v-if="filterLoading" class="flex items-center gap-2 text-slate-400 text-sm py-4">
              <i class="pi pi-spin pi-spinner"></i> Memuat konfigurasi filter…
            </div>
            <div v-else-if="filterError" class="text-sm text-red-500 bg-red-50 rounded-xl p-3">
              <i class="pi pi-exclamation-triangle mr-1"></i> {{ filterError }}
            </div>
            <div
                v-for="group in filterGroups"
                :key="group.title"
                class="filter-group"
            >
                <div class="filter-group-header">
                    <i class="pi pi-folder text-green-600 text-xs"></i>
                    <span class="filter-group-title">
                        {{ group.title }}
                    </span>
                </div>
                <div
                    v-for="field in group.fields"
                    :key="field.key"
                    class="mb-4 last:mb-0"
                >
                    <label class="filter-label">
                        {{ field.label }}
                    </label>
                    <Select
                        v-if="field.type === 'select'"
                        v-model="activeFilters[field.key]"
                        :options="field.options?.value ?? field.options"
                        optionLabel="label"
                        optionValue="value"
                        class="w-full filter-select"
                        appendTo="body"
                    />
                    <InputText
                        v-else-if="field.type === 'text'"
                        v-model="activeFilters[field.key]"
                        :placeholder="field.placeholder"
                        class="w-full"
                    />
                    <InputNumber
                        v-else-if="field.type === 'number'"
                        v-model="activeFilters[field.key]"
                        class="w-full"
                        fluid
                    />
                    <div
                        v-else-if="field.type === 'range'"
                        class="grid grid-cols-2 gap-2"
                    >
                        <InputNumber
                            v-model="activeFilters[field.minKey]"
                            placeholder="Minimum"
                            class="w-full"
                            fluid
                        />

                        <InputNumber
                            v-model="activeFilters[field.maxKey]"
                            placeholder="Maksimum"
                            class="w-full"
                            fluid
                        />
                    </div>
                    <div v-else-if="field.type === 'range-slider'">

                        <div class="flex justify-between text-xs text-slate-500 mb-2">
                            <span>
                                {{ field.prefix ?? '' }}
                                {{ formatValue(activeFilters[field.key][0]) }}
                                {{ field.suffix ?? '' }}
                            </span>

                            <span>
                                {{ field.prefix ?? '' }}
                                {{ formatValue(activeFilters[field.key][1]) }}
                                {{ field.suffix ?? '' }}
                            </span>
                        </div>

                        <Slider
                            v-model="activeFilters[field.key]"
                            range
                            :min="field.min"
                            :max="field.max"
                            :step="field.step ?? 1"
                            class="w-full"
                            @slideend="
                                () => {
                                    if (field.key === 'usia')
                                        usiaTouched = true
                                    else if (field.key === 'jumlah_penyaluran')
                                        penyaluranTouched = true
                                }
                            "
                        />

                    </div>
                    <!-- DATE -->
                    <DatePicker
                        v-else-if="field.type === 'date'"
                        v-model="activeFilters[field.key]"
                        class="w-full"
                    />
                </div>
            </div>
          </div>
          <div class="px-5 py-4 border-t border-slate-100 flex gap-2">
            <Button
              label="Terapkan"
              icon="pi pi-check"
              class="flex-1"
              size="small"
              @click="applyFilter"
            />
            <Button
              label="Reset"
              icon="pi pi-times"
              size="small"
              severity="secondary"
              outlined
              @click="resetFilter"
            />
          </div>
        </div>
      </transition>
    </teleport>
  </AppLayout>
</template>
<script setup>

import { ref, reactive, computed, onMounted } from 'vue'
import AppLayout   from '@/components/layout/AppLayout.vue'
import Button      from 'primevue/button'
import InputText   from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Select      from 'primevue/select'
import DatePicker  from 'primevue/datepicker'
// import { fetchFilterFields } from '@/services/tampilanDtsenService'
import api                   from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { watch } from 'vue'
import Slider from 'primevue/slider'

// ── Drawer state ──────────────────────────────────────────────────────────────
const showFilter    = ref(false)
const filterLoading = ref(false)
const filterError   = ref('')
const filterFields  = ref([])
// const activeFilters = reactive({})
const globalSearch  = ref('')
const authStore = useAuthStore()
const provinsiOptions = ref([])
const kabkotaOptions = ref([])
const kecamatanOptions = ref([])
const kelurahanOptions = ref([])
const lazOptions = ref([])
const provinsiDomisiliOptions = ref([])
const kabkotaDomisiliOptions = ref([])
const kecamatanDomisiliOptions = ref([])
const kelurahanDomisiliOptions = ref([])
const programOptions = ref([])

const usiaTouched = ref(false)
const penyaluranTouched = ref(false)

const formatRupiah = (value) => {
  if (value == null) return '-'

  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

const activeFilters = reactive({
  skala_laz:'',
  laz_kode: '',

  nama:'',
  nik:'',
  kk:'',

  usia: [0, 100],
  jumlah_penyaluran: [0, 100000000],

  usia_min:'',
  usia_max:'',

  jumlah_penyaluran_min:'',
  jumlah_penyaluran_max:'',

  jenis_kelamin: '',
  agama: '',
  desil: '',
  tipe_penerimaan: '',

  provinsi_kode:'',
  kabkota_kode:'',
  kecamatan_kode:'',
  kelurahan_kode:'',

  provinsi_kode_domisili:'',
  kabkota_kode_domisili:'',
  kecamatan_kode_domisili:'',
  kelurahan_kode_domisili:'',

  program_kode: '',
  nama_program: '',
})



const filterGroups = computed(() => {
    const groups = [
        {
            title: 'Lembaga Pemberi',
            fields: [
                {
                    key: 'skala_laz',
                    label: 'Skala Lembaga',
                    type: 'select',
                    options: [
                        { label: 'Semua', value: '' },
                        { label: 'Nasional', value: '1' },
                        { label: 'Provinsi', value: '2' },
                        { label: 'Kabupaten / Kota', value: '3' }
                    ]
                },
                {
                    key: 'laz_kode',
                    label: 'Nama Lembaga',
                    type: 'select',
                    options: lazOptions
                }
            ]
        },
        {
          title: 'Data Pribadi',
          fields: [
            {
                key: 'nama',
                label: 'Nama',
                type: 'text',
                placeholder: 'Cari nama'
            },
            {
                key: 'nik',
                label: 'NIK',
                type: 'text',
                placeholder: 'Masukkan NIK'
            },
            {
                key: 'kk',
                label: 'No. KK',
                type: 'text',
                placeholder: 'Masukkan No KK'
            },
            {
              key: 'jenis_kelamin',
              label: 'Jenis Kelamin',
              type: 'select',
              options: [
                { label: 'Semua', value: '' },
                { label: 'Laki-laki', value: 'm' },
                { label: 'Perempuan', value: 'f' }
              ]
            },
            {
              key: 'agama',
              label: 'Agama',
              type: 'select',
              options: [
                { label: 'Semua', value: '' },
                { label: 'Islam', value: 'Islam' },
                { label: 'Kristen', value: 'Kristen' },
                { label: 'Katolik', value: 'Katolik' },
                { label: 'Hindu', value: 'Hindu' },
                { label: 'Budha', value: 'Budha' },
                { label: 'Konghucu', value: 'Konghucu' }
              ]
            },
            {
                key: 'usia',
                label: 'Rentang Usia',
                type: 'range-slider',
                min: 0,
                max: 100,
                step: 1,
                suffix: ' Tahun'
            },
            {
              key: 'desil',
              label: 'Desil',
              type: 'select',
              options: [
                { label: 'Semua', value: '' },
                { label: 'Desil 1', value: 1 },
                { label: 'Desil 2', value: 2 },
                { label: 'Desil 3', value: 3 },
                { label: 'Desil 4', value: 4 },
                { label: 'Desil 5', value: 5 },
                { label: 'Desil 6', value: 6 },
                { label: 'Desil 7', value: 7 },
                { label: 'Desil 8', value: 8 },
                { label: 'Desil 9', value: 9 },
                { label: 'Desil 10', value: 10 },
                { label: 'Desil N/A', value: 0 }
              ]
            }
          ]
        },
        {
          title: 'Alamat KTP',
          fields: [
            {
              key: 'provinsi_kode',
              label: 'Provinsi',
              type: 'select',
              options: provinsiOptions
            },
            {
              key: 'kabkota_kode',
              label: 'Kabupaten/Kota',
              type: 'select',
              options: kabkotaOptions
            },
            {
              key: 'kecamatan_kode',
              label: 'Kecamatan',
              type: 'select',
              options: kecamatanOptions
            },
            {
              key: 'kelurahan_kode',
              label: 'Kelurahan',
              type: 'select',
              options: kelurahanOptions
            }
          ]
        },
        {
          title: 'Alamat Domisili',
          fields: [
            {
              key: 'provinsi_kode_domisili',
              label: 'Provinsi',
              type: 'select',
              options: provinsiDomisiliOptions
            },
            {
              key: 'kabkota_kode_domisili',
              label: 'Kabupaten/Kota',
              type: 'select',
              options: kabkotaDomisiliOptions
            },
            {
              key: 'kecamatan_kode_domisili',
              label: 'Kecamatan',
              type: 'select',
              options: kecamatanDomisiliOptions
            },
            {
              key: 'kelurahan_kode_domisili',
              label: 'Kelurahan',
              type: 'select',
              options: kelurahanDomisiliOptions
            }
          ]
        },
        {
          title: 'Penyaluran',
          fields: [
            {
                key: 'jumlah_penyaluran',
                label: 'Jumlah Penyaluran',
                type: 'range-slider',
                min: 0,
                max: 100000000,
                step: 50000,
                prefix: 'Rp '
            },
            {
              key: 'tipe_penerimaan',
              label: 'Tipe Penerimaan',
              type: 'select',
              options: [
                  { label:'Semua', value:'' },
                  { label:'Penerima Manfaat Langsung', value:'pml' },
                  { label:'Penerima Manfaat Tidak Langsung', value:'pmtl' }
              ]
            },
            {
              key:'program_kode',
              label:'Bidang',
              type:'select',
              options: programOptions
            },
            {
                key: 'nama_program',
                label: 'Nama Program',
                type: 'text',
                placeholder: 'Masukkan Nama Program'
            }
          ]
        }
    ]
    if (authStore.user?.laz_kode) {
        return groups.filter(g => g.title !== 'Lembaga Pemberi')
    }

    return groups
})

async function loadLaz() {
    activeFilters.laz_kode = ''
    const params = {}
    if (activeFilters.skala_laz) {
        params.skala = activeFilters.skala_laz
    }
    const res = await api.get('/lembaga', { params })
    lazOptions.value = [
        {
            label: 'Semua',
            value: ''
        },
        ...res.data.map(i => ({
            label: i.nama,
            value: i.kode
        }))
    ]
}

async function loadProvinsi() {
    const res = await api.get('/wilayah/provinsi')
    provinsiOptions.value = [
        { label: 'Semua', value: '' },
        ...res.data.data.map(i => ({
            label: i.nama,
            value: i.kode
        }))
    ]
}

async function loadKabKota() {
    activeFilters.kabkota_kode = ''
    activeFilters.kecamatan_kode = ''
    activeFilters.kelurahan_kode = ''
    kecamatanOptions.value = []
    kelurahanOptions.value = []
    if (!activeFilters.provinsi_kode) {
        kabkotaOptions.value = []
        return
    }
    const res = await api.get('/wilayah/kabkota', {
        params: {
            provinsi_kode: activeFilters.provinsi_kode
        }
    })
    kabkotaOptions.value = [
        { label: 'Semua', value: '' },
        ...res.data.data.map(i => ({
            label: i.nama,
            value: i.kode
        }))
    ]
}

async function loadKecamatan() {
    activeFilters.kecamatan_kode = ''
    activeFilters.kelurahan_kode = ''
    kelurahanOptions.value = []
    if (!activeFilters.kabkota_kode) {
        kecamatanOptions.value = []
        return
    }
    const res = await api.get('/wilayah/kecamatan', {
        params: {
            kabkota_kode: activeFilters.kabkota_kode
        }
    })
    kecamatanOptions.value = [
        { label: 'Semua', value: '' },
        ...res.data.data.map(i => ({
            label: i.nama,
            value: i.kode
        }))
    ]
}

async function loadKelurahan() {
    activeFilters.kelurahan_kode = ''
    if (!activeFilters.kecamatan_kode) {
        kelurahanOptions.value = []
        return
    }
    const res = await api.get('/wilayah/kelurahan', {
        params: {
            kecamatan_kode: activeFilters.kecamatan_kode
        }
    })
    kelurahanOptions.value = [
        { label: 'Semua', value: '' },
        ...res.data.data.map(i => ({
            label: i.nama,
            value: i.kode
        }))
    ]
}

async function loadProvinsiDomisili() {
    const res = await api.get('/wilayah/provinsi')
    provinsiDomisiliOptions.value = [
        { label: 'Semua', value: '' },
        ...res.data.data.map(i => ({
            label: i.nama,
            value: i.kode
        }))
    ]
}

async function loadKabKotaDomisili() {
    activeFilters.kabkota_kode_domisili = ''
    activeFilters.kecamatan_kode_domisili = ''
    activeFilters.kelurahan_kode_domisili = ''

    kecamatanDomisiliOptions.value = []
    kelurahanDomisiliOptions.value = []

    if (!activeFilters.provinsi_kode_domisili) {
        kabkotaDomisiliOptions.value = []
        return
    }

    const res = await api.get('/wilayah/kabkota', {
        params: {
            provinsi_kode: activeFilters.provinsi_kode_domisili
        }
    })

    kabkotaDomisiliOptions.value = [
        { label: 'Semua', value: '' },
        ...res.data.data.map(i => ({
            label: i.nama,
            value: i.kode
        }))
    ]
}

async function loadKecamatanDomisili() {
    activeFilters.kecamatan_kode_domisili = ''
    activeFilters.kelurahan_kode_domisili = ''
    kelurahanDomisiliOptions.value = []
    if (!activeFilters.kabkota_kode_domisili) {
        kecamatanDomisiliOptions.value = []
        return
    }
    const res = await api.get('/wilayah/kecamatan', {
        params: {
            kabkota_kode: activeFilters.kabkota_kode_domisili
        }
    })
    kecamatanDomisiliOptions.value = [
        { label: 'Semua', value: '' },
        ...res.data.data.map(i => ({
            label: i.nama,
            value: i.kode
        }))
    ]
}

async function loadKelurahanDomisili() {
    activeFilters.kelurahan_kode_domisili = ''
    if (!activeFilters.kecamatan_kode_domisili) {
        kelurahanDomisiliOptions.value = []
        return
    }
    const res = await api.get('/wilayah/kelurahan', {
        params: {
            kecamatan_kode: activeFilters.kecamatan_kode_domisili
        }
    })
    kelurahanDomisiliOptions.value = [
        { label: 'Semua', value: '' },
        ...res.data.data.map(i => ({
            label: i.nama,
            value: i.kode
        }))
    ]
}

async function loadProgram() {
    const res = await api.get('/bidang')
    programOptions.value = [
        {
            label: 'Semua',
            value: ''
        },
        ...res.data.map(i => ({
            label: i.bidang_label,
            value: i.bidang_kode
        }))
    ]
}

function formatValue(val) {
    return Number(val).toLocaleString('id-ID')
}

watch(() => activeFilters.provinsi_kode, loadKabKota)
watch(() => activeFilters.kabkota_kode, loadKecamatan)
watch(() => activeFilters.kecamatan_kode, loadKelurahan)
watch(() => activeFilters.skala_laz, loadLaz)
watch(() => activeFilters.provinsi_kode_domisili, loadKabKotaDomisili)
watch(() => activeFilters.kabkota_kode_domisili, loadKecamatanDomisili)
watch(() => activeFilters.kecamatan_kode_domisili, loadKelurahanDomisili)

const activeFilterCount = computed(() => {
    let count = 0
    for (const [k, v] of Object.entries(activeFilters)) {
        if (k === 'usia') {
            if (usiaTouched.value) count++
            continue
        }
        if (k === 'jumlah_penyaluran') {
            if (penyaluranTouched.value) count++
            continue
        }
        if (v !== '' && v != null) {
            count++
        }
    }
    return count
})

const groupedFilterFields = computed(() => {
  const groups = {}
  for (const f of filterFields.value) {
    const g = f.field_group || ''
    if (!groups[g]) groups[g] = []
    groups[g].push(f)
  }
  return groups
})



// ── Tabel ─────────────────────────────────────────────────────────────────────
const tableLoading = ref(false)
const tableError   = ref('')
const rows         = ref([])
const pagination   = reactive({ page: 1, perPage: 20, total: 0, totalPages: 1 })

async function fetchMustahik(page = 1) {

  tableLoading.value = true
  tableError.value   = ''

  try {
    const params = {
      page,
      per_page: pagination.perPage,
      laz_kode: authStore.user?.laz_kode
    }
    if (globalSearch.value.trim()) {
      params.nama = globalSearch.value.trim()
    }
    for (const [k, v] of Object.entries(activeFilters)) {
        if (k === 'usia') {
            if (usiaTouched.value) {
                params.usia_min = v[0]
                params.usia_max = v[1]
            }
            continue
        }
        if (k === 'jumlah_penyaluran') {
            if (penyaluranTouched.value) {
                params.jumlah_penyaluran_min = v[0]
                params.jumlah_penyaluran_max = v[1]
            }
            continue
        }
        if (v !== '' && v != null) {
            params[k] = v
        }
    }
    console.log('globalSearch =', globalSearch.value)
    console.log('params =', params)
    const res = await api.get('/mustahik', { params })
    const d = res.data

    rows.value            = d.data ?? d.items ?? []
    pagination.page       = d.meta?.page  ?? page
    pagination.total      = d.meta?.total ?? rows.value.length
    pagination.totalPages = d.meta?.pages ?? 1

  } catch (e) {
    tableError.value = 'Gagal memuat data penerima manfaat: ' + (e?.response?.data?.message ?? e.message)
    console.error(e)
  } finally {
    tableLoading.value = false
  }
}

function applyFilter() {
  showFilter.value = false
  pagination.page  = 1
  fetchMustahik(1)
}

function resetFilter() {

    for (const k of Object.keys(activeFilters))
        activeFilters[k] = ''

    activeFilters.usia = [0,100]
    activeFilters.jumlah_penyaluran = [0,100000000]

    usiaTouched.value = false
    penyaluranTouched.value = false

    globalSearch.value = ''

    loadLaz()
    pagination.page = 1
    fetchMustahik(1)
}

function changePage(p) { fetchMustahik(p) }

onMounted(() => {
  // loadFilterFields()
  fetchMustahik(1)
  loadProvinsi()
  loadLaz()
  loadProvinsiDomisili()
  loadProgram()
})
</script>

<style scoped>
.fade-backdrop-enter-active,
.fade-backdrop-leave-active { transition: opacity 0.25s ease; }
.fade-backdrop-enter-from,
.fade-backdrop-leave-to     { opacity: 0; }

.slide-right-enter-active { transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1); }
.slide-right-leave-active { transition: transform 0.25s cubic-bezier(0.32, 0.72, 0, 1); }
.slide-right-enter-from   { transform: translateX(100%); }
.slide-right-leave-to     { transform: translateX(100%); }

.filter-group{
    background:#fff;
    border:1px solid #dfe6ee;
    border-radius:16px;
    padding:18px;
    box-shadow:0 2px 8px rgba(15,23,42,.04);
}

.filter-group-header{
    display:flex;
    align-items:center;
    gap:12px;
    margin-bottom:16px;
}

.filter-group-header::after{
    content:"";
    flex:1;
    height:1px;
    background:#e2e8f0;
}

.filter-group-title{
    display:flex;
    align-items:center;
    gap:8px;
    font-size:.75rem;
    font-weight:800;
    letter-spacing:.12em;
    color:#16a34a;
    text-transform:uppercase;
}

.filter-label{
    display:block;
    margin-bottom:8px;
    font-size:.82rem;
    font-weight:600;
    color:#475569;
}

.filter-select{
    width:100%;
}
</style>
