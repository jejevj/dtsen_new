<template>
  <AppLayout>
    <div class="space-y-5">

      <!-- Header -->
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 class="text-xl font-bold text-slate-800">Data Baseline</h2>
          <p class="text-sm text-slate-500 mt-0.5">Data baseline penerima manfaat ZAWA · Sumber: Kemenag</p>
        </div>

        <!-- Tombol Filter (hanya aktif jika provinsi sudah dipilih) -->
        <Button
          icon="pi pi-filter"
          severity="primary"
          outlined
          size="small"
          :disabled="!currentProvinsi"
          v-tooltip="!currentProvinsi ? 'Pilih provinsi terlebih dahulu' : ''"
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

      <!-- Tab switcher -->
      <div class="flex gap-1 bg-slate-100 rounded-xl p-1 w-fit">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="switchTab(tab.key)"
          :class="[
            'px-5 py-2 rounded-lg text-sm font-semibold transition-all',
            activeTab === tab.key
              ? 'bg-white text-primary-700 shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
          ]"
        >
          <i :class="tab.icon + ' mr-1.5'"></i>{{ tab.label }}
        </button>
      </div>

      <!-- TAB ANGGOTA -->
      <template v-if="activeTab === 'anggota'">
        <div class="bg-white border border-slate-200 rounded-2xl shadow-sm px-5 py-4">
          <div class="flex flex-wrap items-end gap-4">

            <!-- Provinsi -->
            <div class="flex flex-col gap-1 min-w-[200px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Provinsi</label>
              <Select
                v-model="anggota.provinsi"
                :options="provinsiOptions"
                option-label="label"
                option-value="slug"
                placeholder="Pilih Provinsi…"
                class="w-full text-sm"
                :loading="wilayahLoading"
                filter show-clear
                @change="handleAnggotaProvinsiChange"
              />
            </div>

            <!-- Kabkota -->
            <div v-if="anggota.provinsi" class="flex flex-col gap-1 min-w-[220px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Kabupaten / Kota</label>
              <Select
                v-model="anggota.kabkota"
                :options="anggotaKabkotaOptions"
                option-label="nama" option-value="kode"
                placeholder="Semua Kab/Kota"
                class="w-full text-sm" :loading="anggotaKabkotaLoading"
                filter show-clear
                @change="handleAnggotaKabkotaChange"
              />
            </div>

            <!-- Kecamatan -->
            <div v-if="anggota.kabkota" class="flex flex-col gap-1 min-w-[220px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Kecamatan</label>
              <Select
                v-model="anggota.kecamatan"
                :options="anggotaKecamatanOptions"
                option-label="nama" option-value="kode"
                placeholder="Semua Kecamatan"
                class="w-full text-sm" :loading="anggotaKecamatanLoading"
                filter show-clear
              />
            </div>

            <!-- Search -->
            <div class="flex flex-col gap-1 flex-1 min-w-[180px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Cari (halaman ini)</label>
              <InputText
                v-model="anggota.search"
                placeholder="Nama / NIK…"
                class="text-sm w-full"
                @keyup.enter="loadAnggota()"
              />
            </div>

            <!-- Tombol -->
            <div class="flex gap-2 pb-0.5">
              <Button
                label="Tampilkan" icon="pi pi-search" size="small"
                :loading="anggota.loading"
                @click="loadAnggota()"
              />
              <Button
                label="Reset" icon="pi pi-times" size="small"
                severity="secondary" outlined
                @click="resetAnggota"
              />
            </div>
          </div>

          <!-- Badge filter aktif -->
          <div v-if="activeFilterCount > 0" class="mt-3 flex items-center gap-2 flex-wrap">
            <span class="text-xs text-slate-500">Filter aktif:</span>
            <span
              v-for="(item, idx) in activeFiltersBadges"
              :key="idx"
              class="inline-flex items-center gap-1 px-2 py-0.5 bg-primary-50 text-primary-700 border border-primary-200 text-xs font-semibold rounded-full"
            >
              {{ item.label }}: {{ item.display }}
              <button class="ml-0.5 hover:text-primary-900" @click="clearOneFilter(item.key)">
                <i class="pi pi-times text-[10px]"></i>
              </button>
            </span>
          </div>
        </div>

        <BaselineTable
          type="anggota"
          :loading="anggota.loading" :error="anggota.error"
          :rows="anggota.rows" :columns="anggota.columns"
          :meta="anggota.meta" :history-stack="anggota.historyStack"
          empty-hint="Tidak ada data yang sesuai."
          title="Data Anggota"
          @next="nextAnggota" @prev="prevAnggota"
          @detail="goToAnggotaDetail"
        />
      </template>

      <!-- TAB KELUARGA -->
      <template v-if="activeTab === 'keluarga'">
        <div class="bg-white border border-slate-200 rounded-2xl shadow-sm px-5 py-4">
          <div class="flex flex-wrap items-end gap-4">

            <!-- Provinsi -->
            <div class="flex flex-col gap-1 min-w-[200px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Provinsi</label>
              <Select
                v-model="keluarga.provinsi"
                :options="provinsiOptions"
                option-label="label"
                option-value="slug"
                placeholder="Pilih Provinsi…"
                class="w-full text-sm"
                :loading="wilayahLoading"
                filter show-clear
                @change="handleKeluargaProvinsiChange"
              />
            </div>

            <!-- Kabkota -->
            <div v-if="keluarga.provinsi" class="flex flex-col gap-1 min-w-[220px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Kabupaten / Kota</label>
              <Select
                v-model="keluarga.kabkota"
                :options="keluargaKabkotaOptions"
                option-label="nama" option-value="kode"
                placeholder="Semua Kab/Kota"
                class="w-full text-sm" :loading="keluargaKabkotaLoading"
                filter show-clear
                @change="handleKeluargaKabkotaChange"
              />
            </div>

            <!-- Kecamatan -->
            <div v-if="keluarga.kabkota" class="flex flex-col gap-1 min-w-[220px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Kecamatan</label>
              <Select
                v-model="keluarga.kecamatan"
                :options="keluargaKecamatanOptions"
                option-label="nama" option-value="kode"
                placeholder="Semua Kecamatan"
                class="w-full text-sm" :loading="keluargaKecamatanLoading"
                filter show-clear
              />
            </div>

            <!-- Search -->
            <div class="flex flex-col gap-1 flex-1 min-w-[180px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Cari (halaman ini)</label>
              <InputText
                v-model="keluarga.search"
                placeholder="No. KK / Nama…"
                class="text-sm w-full"
                @keyup.enter="loadKeluarga()"
              />
            </div>

            <!-- Tombol -->
            <div class="flex gap-2 pb-0.5">
              <Button
                label="Tampilkan" icon="pi pi-search" size="small"
                :loading="keluarga.loading"
                @click="loadKeluarga()"
              />
              <Button
                label="Reset" icon="pi pi-times" size="small"
                severity="secondary" outlined
                @click="resetKeluarga"
              />
            </div>
          </div>

          <!-- Badge filter aktif -->
          <div v-if="activeFilterCount > 0" class="mt-3 flex items-center gap-2 flex-wrap">
            <span class="text-xs text-slate-500">Filter aktif:</span>
            <span
              v-for="(item, idx) in activeFiltersBadges"
              :key="idx"
              class="inline-flex items-center gap-1 px-2 py-0.5 bg-primary-50 text-primary-700 border border-primary-200 text-xs font-semibold rounded-full"
            >
              {{ item.label }}: {{ item.display }}
              <button class="ml-0.5 hover:text-primary-900" @click="clearOneFilter(item.key)">
                <i class="pi pi-times text-[10px]"></i>
              </button>
            </span>
          </div>
        </div>

        <BaselineTable
          type="keluarga"
          :loading="keluarga.loading" :error="keluarga.error"
          :rows="keluarga.rows" :columns="keluarga.columns"
          :meta="keluarga.meta" :history-stack="keluarga.historyStack"
          empty-hint="Tidak ada data yang sesuai."
          title="Data Keluarga"
          @next="nextKeluarga" @prev="prevKeluarga"
          @detail="goToKeluargaDetail"
        />
      </template>

    </div>

    <!-- ===== DRAWER FILTER (dari kanan) ===== -->
    <teleport to="body">
      <!-- Backdrop -->
      <transition name="fade-backdrop">
        <div
          v-if="showFilter"
          class="fixed inset-0 bg-black/30 z-40"
          @click="showFilter = false"
        />
      </transition>

      <!-- Panel -->
      <transition name="slide-right">
        <div
          v-if="showFilter"
          class="fixed top-0 right-0 h-full w-full max-w-md bg-white shadow-2xl z-50 flex flex-col"
        >
          <!-- Header drawer -->
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

          <!-- Body drawer (scrollable) -->
          <div class="flex-1 overflow-y-auto px-5 py-4 space-y-5">

            <!-- Pemberitahuan jika provinsi belum dipilih -->
            <div v-if="!currentProvinsi" class="flex items-center gap-2 text-amber-600 bg-amber-50 border border-amber-200 rounded-xl p-3 text-sm">
              <i class="pi pi-exclamation-triangle shrink-0"></i>
              <span>Pilih provinsi terlebih dahulu untuk mengaktifkan filter.</span>
            </div>

            <!-- Loading konfigurasi -->
            <div v-else-if="filterLoading" class="flex items-center gap-2 text-slate-400 text-sm py-4">
              <i class="pi pi-spin pi-spinner"></i> Memuat konfigurasi filter…
            </div>

            <!-- Error konfigurasi -->
            <div v-else-if="filterError" class="text-sm text-red-500 bg-red-50 rounded-xl p-3">
              <i class="pi pi-exclamation-triangle mr-1"></i> {{ filterError }}
            </div>

            <template v-else>
              <!-- Group per field_group -->
              <div
                v-for="(groupFields, groupName) in groupedFilterFields"
                :key="groupName"
                class="space-y-3"
              >
                <p v-if="groupName" class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ groupName }}</p>

                <div v-for="field in groupFields" :key="field.field_key">
                  <label class="block text-xs font-medium text-slate-600 mb-1">{{ field.field_label }}</label>

                  <!-- Dropdown jika ada refs -->
                  <Select
                    v-if="field.refs && field.refs.length"
                    v-model="currentFilters[field.field_key]"
                    :options="[{ ref_value: '', ref_label: 'Semua' }, ...field.refs]"
                    option-label="ref_label"
                    option-value="ref_value"
                    :placeholder="'Semua ' + field.field_label"
                    class="w-full text-sm"
                    show-clear
                  />

                  <!-- Angka -->
                  <InputNumber
                    v-else-if="field.field_type === 'Integer' || field.field_type === 'Float'"
                    v-model="currentFilters[field.field_key]"
                    :placeholder="field.field_label"
                    class="w-full"
                    :min-fraction-digits="field.field_type === 'Float' ? 2 : 0"
                    :max-fraction-digits="field.field_type === 'Float' ? 2 : 0"
                  />

                  <!-- Tanggal -->
                  <DatePicker
                    v-else-if="field.field_type === 'Date'"
                    v-model="currentFilters[field.field_key]"
                    :placeholder="field.field_label"
                    date-format="dd/mm/yy"
                    class="w-full"
                    show-button-bar
                  />

                  <!-- Teks -->
                  <InputText
                    v-else
                    v-model="currentFilters[field.field_key]"
                    :placeholder="'Cari ' + field.field_label"
                    class="w-full text-sm"
                  />
                </div>
              </div>

              <!-- Kosong -->
              <div v-if="!filterFields.length" class="text-sm text-slate-400 py-4">
                <i class="pi pi-info-circle mr-1"></i>
                Belum ada field filter yang dikonfigurasi.
              </div>
            </template>
          </div>

          <!-- Footer drawer -->
          <div class="px-5 py-4 border-t border-slate-100 flex gap-2">
            <Button
              label="Terapkan"
              icon="pi pi-check"
              class="flex-1"
              size="small"
              :disabled="!currentProvinsi"
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout     from '@/components/layout/AppLayout.vue'
import BaselineTable from '@/components/baseline/BaselineTable.vue'
import Button        from 'primevue/button'
import InputText     from 'primevue/inputtext'
import InputNumber   from 'primevue/inputnumber'
import Select        from 'primevue/select'
import DatePicker    from 'primevue/datepicker'
import {
  fetchBaselineProvinsi,
  fetchKabkotaByBps,
  fetchKecamatan,
  fetchBaselineAnggota,
  fetchBaselineKeluarga,
} from '@/services/baselineService'
import { fetchFilterFields } from '@/services/tampilanDtsenService'

const router = useRouter()

function goToAnggotaDetail(row) {
  const nik = row.nomor_induk_kependudukan || row.nik || row.id
  if (!nik) return
  router.push({ name: 'baseline-anggota-detail', params: { nik: String(nik) } })
}
function goToKeluargaDetail(row) {
  const nkk = row.nomor_kartu_keluarga || row.nkk || row.id
  if (!nkk) return
  router.push({ name: 'baseline-keluarga-detail', params: { nkk: String(nkk) } })
}

// ── Tabs
const tabs = [
  { key: 'anggota',  label: 'Anggota',  icon: 'pi pi-users' },
  { key: 'keluarga', label: 'Keluarga', icon: 'pi pi-home' },
]
const activeTab = ref('anggota')

function switchTab(key) {
  if (activeTab.value === key) return
  activeTab.value = key
}

// ── Computed: provinsi aktif sesuai tab yang sedang ditampilkan
const currentProvinsi = computed(() =>
  activeTab.value === 'anggota' ? anggota.provinsi : keluarga.provinsi
)

// ── Provinsi (shared)
const wilayahLoading  = ref(false)
const provinsiOptions = ref([])

function getProvinsiBps(slug) {
  if (!slug) return null
  return provinsiOptions.value.find(p => p.slug === slug)?.kode ?? null
}

async function loadWilayah() {
  wilayahLoading.value = true
  try {
    const list = await fetchBaselineProvinsi()
    provinsiOptions.value = list
    if (list.length > 0) {
      const defaultSlug = list[0].slug
      const defaultBps  = list[0].kode
      anggota.provinsi  = defaultSlug
      keluarga.provinsi = defaultSlug
      loadAnggotaKabkota(defaultBps)
      loadKeluargaKabkota(defaultBps)
      loadAnggota()
      loadKeluarga()
    }
  } catch (e) {
    console.error('[Wilayah] gagal load provinsi:', e)
  } finally {
    wilayahLoading.value = false
  }
}

// ── Wilayah helpers — Anggota
const anggotaKabkotaOptions   = ref([])
const anggotaKecamatanOptions = ref([])
const anggotaKabkotaLoading   = ref(false)
const anggotaKecamatanLoading = ref(false)

async function loadAnggotaKabkota(bpsKode) {
  anggotaKabkotaOptions.value = []
  if (!bpsKode) return
  anggotaKabkotaLoading.value = true
  try { anggotaKabkotaOptions.value = await fetchKabkotaByBps(bpsKode) }
  catch (e) { console.error('[Wilayah] kabkota anggota:', e) }
  finally { anggotaKabkotaLoading.value = false }
}

function handleAnggotaProvinsiChange() {
  anggota.kabkota   = ''
  anggota.kecamatan = ''
  anggotaKecamatanOptions.value = []
  const bps = getProvinsiBps(anggota.provinsi)
  loadAnggotaKabkota(bps)
  loadAnggota()
}

function handleAnggotaKabkotaChange() {
  anggota.kecamatan = ''
  anggotaKecamatanOptions.value = []
  if (!anggota.kabkota) return
  anggotaKecamatanLoading.value = true
  fetchKecamatan(anggota.kabkota)
    .then(r => { anggotaKecamatanOptions.value = r })
    .catch(e => console.error('[Wilayah] kecamatan anggota:', e))
    .finally(() => { anggotaKecamatanLoading.value = false })
}

// ── Wilayah helpers — Keluarga
const keluargaKabkotaOptions   = ref([])
const keluargaKecamatanOptions = ref([])
const keluargaKabkotaLoading   = ref(false)
const keluargaKecamatanLoading = ref(false)

async function loadKeluargaKabkota(bpsKode) {
  keluargaKabkotaOptions.value = []
  if (!bpsKode) return
  keluargaKabkotaLoading.value = true
  try { keluargaKabkotaOptions.value = await fetchKabkotaByBps(bpsKode) }
  catch (e) { console.error('[Wilayah] kabkota keluarga:', e) }
  finally { keluargaKabkotaLoading.value = false }
}

function handleKeluargaProvinsiChange() {
  keluarga.kabkota   = ''
  keluarga.kecamatan = ''
  keluargaKecamatanOptions.value = []
  const bps = getProvinsiBps(keluarga.provinsi)
  loadKeluargaKabkota(bps)
  loadKeluarga()
}

function handleKeluargaKabkotaChange() {
  keluarga.kecamatan = ''
  keluargaKecamatanOptions.value = []
  if (!keluarga.kabkota) return
  keluargaKecamatanLoading.value = true
  fetchKecamatan(keluarga.kabkota)
    .then(r => { keluargaKecamatanOptions.value = r })
    .catch(e => console.error('[Wilayah] kecamatan keluarga:', e))
    .finally(() => { keluargaKecamatanLoading.value = false })
}

// ── Table state factory
function makeTableState() {
  return reactive({
    loading: false, error: '',
    rows: [], columns: [],
    search: '',
    provinsi:  '',
    kabkota:   '',
    kecamatan: '',
    historyStack: [], currentCursor: null,
    meta: {
      label: '', totalItems: 0, totalPages: 1, currentPage: 1,
      hasNextPage: false, hasPreviousPage: false, nextCursor: null, limit: 10,
    },
  })
}

const anggota  = makeTableState()
const keluarga = makeTableState()

// ── Drawer Filter state
// Pisah filter per tab agar tidak cross-contaminate
const showFilter    = ref(false)
const filterLoading = ref(false)
const filterError   = ref('')
const filterFields  = ref([])

// Filter anggota (individu) dan filter keluarga disimpan terpisah
const anggotaFilters  = reactive({})
const keluargaFilters = reactive({})

// currentFilters mengarah ke store yang sesuai tab aktif
const currentFilters = computed(() =>
  activeTab.value === 'anggota' ? anggotaFilters : keluargaFilters
)

// Jumlah filter aktif untuk tab yang sedang aktif
const activeFilterCount = computed(() =>
  Object.values(currentFilters.value).filter(v => v !== '' && v != null).length
)

/**
 * Format nilai filter untuk dikirim ke backend:
 * - Date object → string YYYY-MM-DD
 * - Nilai lain → string
 */
function formatFilterValue(val) {
  if (val instanceof Date) {
    const y = val.getFullYear()
    const m = String(val.getMonth() + 1).padStart(2, '0')
    const d = String(val.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
  }
  return String(val)
}

// Badge filter: array of { key, label, display } untuk tab aktif
const activeFiltersBadges = computed(() => {
  const result = []
  for (const f of filterFields.value) {
    const val = currentFilters.value[f.field_key]
    if (val === '' || val == null) continue
    // Cari label display untuk nilai dropdown (refs)
    let display = formatFilterValue(val)
    if (f.refs && f.refs.length) {
      const ref = f.refs.find(r => r.ref_value === String(val))
      if (ref) display = ref.ref_label
    }
    result.push({ key: f.field_key, label: f.field_label, display })
  }
  return result
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

// Kategori filter sesuai tab aktif
const filterKategori = computed(() =>
  activeTab.value === 'anggota' ? 'individu' : 'keluarga'
)

async function loadFilterFields() {
  if (!currentProvinsi.value) return
  filterLoading.value = true
  filterError.value   = ''
  try {
    const data = await fetchFilterFields(filterKategori.value)
    filterFields.value = data
    // Inisialisasi key yang belum ada di currentFilters
    const store = activeTab.value === 'anggota' ? anggotaFilters : keluargaFilters
    for (const f of data) {
      if (!(f.field_key in store)) store[f.field_key] = ''
    }
  } catch (e) {
    filterError.value = 'Gagal memuat konfigurasi filter.'
    console.error('[DataBaseline] fetchFilterFields error:', e)
  } finally {
    filterLoading.value = false
  }
}

// Reload filter fields saat tab berganti
watch(activeTab, () => {
  // Reset fields agar drawer menampilkan field yang sesuai tab baru
  filterFields.value = []
  if (currentProvinsi.value) {
    loadFilterFields()
  }
})

// Load filter fields saat drawer dibuka (lazy)
watch(showFilter, (val) => {
  if (val && filterFields.value.length === 0 && currentProvinsi.value) {
    loadFilterFields()
  }
})

function applyFilter() {
  showFilter.value = false
  if (activeTab.value === 'anggota') loadAnggota()
  else loadKeluarga()
}

function resetFilter() {
  // Reset hanya filter tab aktif
  const store = activeTab.value === 'anggota' ? anggotaFilters : keluargaFilters
  for (const k of Object.keys(store)) store[k] = ''
  showFilter.value = false
  if (activeTab.value === 'anggota') loadAnggota()
  else loadKeluarga()
}

function clearOneFilter(fieldKey) {
  const store = activeTab.value === 'anggota' ? anggotaFilters : keluargaFilters
  if (fieldKey in store) {
    store[fieldKey] = ''
    applyFilter()
  }
}

// ── Helper: build extra filter params untuk dikirim ke backend
function buildFilterParams(store) {
  const params = {}
  for (const [k, v] of Object.entries(store)) {
    if (v !== '' && v != null) {
      params[k] = formatFilterValue(v)
    }
  }
  return params
}

// ── Anggota
async function loadAnggota(cursor = null) {
  if (!anggota.provinsi) return
  anggota.loading = true; anggota.error = ''
  try {
    const params = {
      provinsi: anggota.provinsi,
      cursor:   cursor || undefined,
      search:   anggota.search.trim() || undefined,
    }
    if (anggota.kabkota)   params.kabkota_kode   = anggota.kabkota
    if (anggota.kecamatan) params.kecamatan_kode = anggota.kecamatan
    // Gabungkan filter aktif tab anggota
    Object.assign(params, buildFilterParams(anggotaFilters))
    const res = await fetchBaselineAnggota(params)
    anggota.rows = res.data ?? []; anggota.columns = res.columns ?? []
    Object.assign(anggota.meta, res.meta ?? {})
    anggota.currentCursor = cursor
  } catch (e) {
    anggota.error = 'Gagal memuat: ' + (e?.response?.data?.error ?? e.message)
  } finally { anggota.loading = false }
}
function nextAnggota() {
  anggota.historyStack.push(anggota.currentCursor)
  loadAnggota(anggota.meta.nextCursor)
}
function prevAnggota() {
  if (anggota.historyStack.length) loadAnggota(anggota.historyStack.pop())
}
function resetAnggota() {
  const first = provinsiOptions.value[0]
  anggota.provinsi  = first?.slug ?? ''
  anggota.kabkota   = ''
  anggota.kecamatan = ''
  anggota.search    = ''
  anggota.rows = []; anggota.columns = []
  anggota.historyStack = []; anggota.currentCursor = null
  anggotaKabkotaOptions.value   = []
  anggotaKecamatanOptions.value = []
  // Reset filter anggota
  for (const k of Object.keys(anggotaFilters)) anggotaFilters[k] = ''
  Object.assign(anggota.meta, {
    label:'', totalItems:0, totalPages:1, currentPage:1,
    hasNextPage:false, hasPreviousPage:false, nextCursor:null, limit:10,
  })
  if (first) { loadAnggotaKabkota(first.kode); loadAnggota() }
}

// ── Keluarga
async function loadKeluarga(cursor = null) {
  if (!keluarga.provinsi) return
  keluarga.loading = true; keluarga.error = ''
  try {
    const params = {
      provinsi: keluarga.provinsi,
      cursor:   cursor || undefined,
      search:   keluarga.search.trim() || undefined,
    }
    if (keluarga.kabkota)   params.kabkota_kode   = keluarga.kabkota
    if (keluarga.kecamatan) params.kecamatan_kode = keluarga.kecamatan
    // Gabungkan filter aktif tab keluarga
    Object.assign(params, buildFilterParams(keluargaFilters))
    const res = await fetchBaselineKeluarga(params)
    keluarga.rows = res.data ?? []; keluarga.columns = res.columns ?? []
    Object.assign(keluarga.meta, res.meta ?? {})
    keluarga.currentCursor = cursor
  } catch (e) {
    keluarga.error = 'Gagal memuat: ' + (e?.response?.data?.error ?? e.message)
  } finally { keluarga.loading = false }
}
function nextKeluarga() {
  keluarga.historyStack.push(keluarga.currentCursor)
  loadKeluarga(keluarga.meta.nextCursor)
}
function prevKeluarga() {
  if (keluarga.historyStack.length) loadKeluarga(keluarga.historyStack.pop())
}
function resetKeluarga() {
  const first = provinsiOptions.value[0]
  keluarga.provinsi  = first?.slug ?? ''
  keluarga.kabkota   = ''
  keluarga.kecamatan = ''
  keluarga.search    = ''
  keluarga.rows = []; keluarga.columns = []
  keluarga.historyStack = []; keluarga.currentCursor = null
  keluargaKabkotaOptions.value   = []
  keluargaKecamatanOptions.value = []
  // Reset filter keluarga
  for (const k of Object.keys(keluargaFilters)) keluargaFilters[k] = ''
  Object.assign(keluarga.meta, {
    label:'', totalItems:0, totalPages:1, currentPage:1,
    hasNextPage:false, hasPreviousPage:false, nextCursor:null, limit:10,
  })
  if (first) { loadKeluargaKabkota(first.kode); loadKeluarga() }
}

onMounted(() => loadWilayah())
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
</style>
