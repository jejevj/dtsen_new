<template>
  <AppLayout>
    <div class="space-y-5">

      <!-- Header -->
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 class="text-xl font-bold text-slate-800">Data DTSEN</h2>
          <p class="text-sm text-slate-500 mt-0.5">Data DTSEN penerima manfaat ZAWA · Sumber: Kemenag</p>
        </div>

        <!-- Tombol Filter -->
        <button
          :disabled="!currentProvinsi"
          v-tooltip="!currentProvinsi ? 'Pilih provinsi terlebih dahulu' : 'Buka filter pencarian'"
          @click="showFilter = true"
          :class="[
            'inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all border shadow-sm',
            activeFilterCount > 0
              ? 'bg-primary-600 text-white border-primary-600 hover:bg-primary-700 shadow-primary-200'
              : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50 hover:border-slate-300',
            !currentProvinsi ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'
          ]"
        >
          <i class="pi pi-filter text-base"></i>
          <span>Filter</span>
          <span
            v-if="activeFilterCount > 0"
            class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-white text-primary-700 text-[11px] font-bold"
          >{{ activeFilterCount }}</span>
        </button>
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
            <div class="flex flex-col gap-1 min-w-[200px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Provinsi</label>
              <Select
                v-model="anggota.provinsi"
                :options="provinsiOptions"
                option-label="label" option-value="slug"
                placeholder="Pilih Provinsi…"
                class="w-full text-sm" :loading="wilayahLoading"
                filter show-clear
                @change="handleAnggotaProvinsiChange"
              />
            </div>
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
            <div class="flex gap-2 pb-0.5">
              <Button label="Tampilkan" icon="pi pi-search" size="small" :loading="anggota.loading" @click="loadAnggota()" />
              <Button label="Reset" icon="pi pi-times" size="small" severity="secondary" outlined @click="resetAnggota" />
            </div>
          </div>
          <div v-if="activeFilterCount > 0" class="mt-3 flex items-center gap-2 flex-wrap">
            <span class="text-xs text-slate-500">Filter aktif:</span>
            <span
              v-for="(item, idx) in activeFiltersBadges" :key="idx"
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
          empty-hint="Tidak ada data yang sesuai." title="Data Anggota"
          @next="nextAnggota" @prev="prevAnggota" @detail="goToAnggotaDetail"
        />
      </template>

      <!-- TAB KELUARGA -->
      <template v-if="activeTab === 'keluarga'">
        <div class="bg-white border border-slate-200 rounded-2xl shadow-sm px-5 py-4">
          <div class="flex flex-wrap items-end gap-4">
            <div class="flex flex-col gap-1 min-w-[200px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Provinsi</label>
              <Select
                v-model="keluarga.provinsi"
                :options="provinsiOptions"
                option-label="label" option-value="slug"
                placeholder="Pilih Provinsi…"
                class="w-full text-sm" :loading="wilayahLoading"
                filter show-clear
                @change="handleKeluargaProvinsiChange"
              />
            </div>
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
            <div class="flex flex-col gap-1 min-w-[200px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Desil</label>
              <Select
                v-model="keluarga.desil"
                :options="desilOptions"
                option-label="label" option-value="value"
                placeholder="Semua Desil"
                class="w-full text-sm" show-clear
              />
            </div>
            <div class="flex gap-2 pb-0.5">
              <Button label="Tampilkan" icon="pi pi-search" size="small" :loading="keluarga.loading" @click="loadKeluarga()" />
              <Button label="Reset" icon="pi pi-times" size="small" severity="secondary" outlined @click="resetKeluarga" />
            </div>
          </div>
          <div v-if="activeFilterCount > 0" class="mt-3 flex items-center gap-2 flex-wrap">
            <span class="text-xs text-slate-500">Filter aktif:</span>
            <span
              v-for="(item, idx) in activeFiltersBadges" :key="idx"
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
          empty-hint="Tidak ada data yang sesuai." title="Data Keluarga"
          @next="nextKeluarga" @prev="prevKeluarga" @detail="goToKeluargaDetail"
        />
      </template>

    </div>

    <!-- ===== DRAWER FILTER ===== -->
    <teleport to="body">
      <transition name="fade-backdrop">
        <div v-if="showFilter" class="fixed inset-0 bg-black/30 z-40" @click="showFilter = false" />
      </transition>

      <transition name="slide-right">
        <div v-if="showFilter" class="fixed top-0 right-0 h-full w-full max-w-md bg-white shadow-2xl z-50 flex flex-col">

          <!-- Header -->
          <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100">
            <div class="flex items-center gap-2">
              <i class="pi pi-filter text-primary-600"></i>
              <span class="font-semibold text-slate-800">Filter Pencarian</span>
              <span v-if="activeFilterCount > 0" class="px-2 py-0.5 bg-primary-600 text-white text-xs font-bold rounded-full">{{ activeFilterCount }}</span>
            </div>
            <button class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100 text-slate-500 transition" @click="showFilter = false">
              <i class="pi pi-times text-sm"></i>
            </button>
          </div>

          <!-- Body -->
          <div class="flex-1 overflow-y-auto px-5 py-4 space-y-5">

            <div v-if="!currentProvinsi" class="flex items-center gap-2 text-amber-600 bg-amber-50 border border-amber-200 rounded-xl p-3 text-sm">
              <i class="pi pi-exclamation-triangle shrink-0"></i>
              <span>Pilih provinsi terlebih dahulu untuk mengaktifkan filter.</span>
            </div>

            <div v-else-if="filterLoading" class="flex items-center gap-2 text-slate-400 text-sm py-4">
              <i class="pi pi-spin pi-spinner"></i> Memuat konfigurasi filter…
            </div>

            <div v-else-if="filterError" class="text-sm text-red-500 bg-red-50 rounded-xl p-3">
              <i class="pi pi-exclamation-triangle mr-1"></i> {{ filterError }}
            </div>

            <template v-else>

              <!-- Desil — hardcode, keluarga only -->
              <div v-if="activeTab === 'keluarga'" class="space-y-3">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Kesejahteraan</p>
                <div>
                  <label class="block text-xs font-medium text-slate-600 mb-1">Desil</label>
                  <Select
                    v-model="keluarga.desil"
                    :options="desilOptions"
                    option-label="label" option-value="value"
                    placeholder="Semua Desil"
                    class="w-full text-sm" show-clear
                  />
                </div>
              </div>

              <!-- Grup dari DB — semua grup KECUALI yang semua field-nya ternak -->
              <div
                v-for="(groupFields, groupName) in groupedFilterFieldsNoTernak"
                :key="groupName"
                class="space-y-3"
              >
                <p v-if="groupName" class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ groupName }}</p>

                <div v-for="field in groupFields" :key="field.field_key">
                  <label class="block text-xs font-medium text-slate-600 mb-1">{{ field.field_label }}</label>

                  <Select
                    v-if="field.refs && field.refs.length"
                    v-model="currentFilters[field.field_key]"
                    :options="[{ ref_value: '', ref_label: 'Semua' }, ...field.refs]"
                    option-label="ref_label" option-value="ref_value"
                    :placeholder="'Semua ' + field.field_label"
                    class="w-full text-sm" show-clear
                  />

                  <InputNumber
                    v-else-if="field.field_type === 'Integer' || field.field_type === 'Float'"
                    v-model="currentFilters[field.field_key]"
                    :placeholder="field.field_label"
                    class="w-full"
                    :min-fraction-digits="field.field_type === 'Float' ? 2 : 0"
                    :max-fraction-digits="field.field_type === 'Float' ? 2 : 0"
                  />

                  <DatePicker
                    v-else-if="field.field_type === 'Date'"
                    v-model="currentFilters[field.field_key]"
                    :placeholder="field.field_label"
                    date-format="dd/mm/yy"
                    class="w-full" show-button-bar
                  />

                  <InputText
                    v-else
                    v-model="currentFilters[field.field_key]"
                    :placeholder="'Cari ' + field.field_label"
                    class="w-full text-sm"
                  />
                </div>
              </div>

              <!-- Ternak slider — SELALU paling bawah, keluarga only -->
              <div v-if="activeTab === 'keluarga'" class="space-y-4">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Ternak</p>
                <div v-for="tf in TERNAK_FIELDS" :key="tf.key" class="space-y-2">
                  <div class="flex items-center justify-between">
                    <label class="text-xs font-medium text-slate-600">{{ tf.label }}</label>
                    <span class="text-xs font-semibold text-primary-600 bg-primary-50 px-2 py-0.5 rounded-full">
                      {{ ternakSliders[tf.key][0] }} – {{ ternakSliders[tf.key][1] }}
                    </span>
                  </div>
                  <Slider
                    v-model="ternakSliders[tf.key]"
                    :range="true" :min="0" :max="100" :step="1"
                    class="w-full"
                  />
                  <div class="flex justify-between text-[10px] text-slate-400">
                    <span>0</span><span>100</span>
                  </div>
                </div>
              </div>

              <div v-if="activeTab !== 'keluarga' && !filterFields.length" class="text-sm text-slate-400 py-4">
                <i class="pi pi-info-circle mr-1"></i>
                Belum ada field filter yang dikonfigurasi.
              </div>

            </template>
          </div>

          <!-- Footer -->
          <div class="px-5 py-4 border-t border-slate-100 flex gap-2">
            <Button label="Terapkan" icon="pi pi-check" class="flex-1" size="small" :disabled="!currentProvinsi" @click="applyFilter" />
            <Button label="Reset" icon="pi pi-times" size="small" severity="secondary" outlined @click="resetFilter" />
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
import Slider        from 'primevue/slider'
import {
  fetchBaselineProvinsi, fetchKabkotaByBps, fetchKecamatan,
  fetchBaselineAnggota, fetchBaselineKeluarga,
} from '@/services/baselineService'
import { fetchFilterFields } from '@/services/tampilanDtsenService'

const router = useRouter()

// ── Ternak slider config
const TERNAK_FIELDS = [
  { key: 'jumlah_ternak_babi',          label: 'Jumlah Ternak: Babi' },
  { key: 'jumlah_ternak_kambing_domba', label: 'Jumlah Ternak: Kambing / Domba' },
  { key: 'jumlah_ternak_kerbau',        label: 'Jumlah Ternak: Kerbau' },
  { key: 'jumlah_ternak_kuda',          label: 'Jumlah Ternak: Kuda' },
  { key: 'jumlah_ternak_sapi',          label: 'Jumlah Ternak: Sapi' },
]
const TERNAK_KEYS = new Set(TERNAK_FIELDS.map(f => f.key))

const ternakSliders = reactive(
  Object.fromEntries(TERNAK_FIELDS.map(f => [f.key, [0, 100]]))
)

function isTernakField(fieldKey) {
  return TERNAK_KEYS.has(fieldKey)
}

function sliderToApiValue(min, max) {
  if (min === 0 && max === 100) return null
  if (min === max) return String(min)
  return `${min}-${max}`
}

const desilOptions = [
  { value: '1',  label: 'Desil 1' },
  { value: '2',  label: 'Desil 2' },
  { value: '3',  label: 'Desil 3' },
  { value: '4',  label: 'Desil 4' },
  { value: '5',  label: 'Desil 5' },
  { value: '6',  label: 'Desil 6' },
  { value: '7',  label: 'Desil 7' },
  { value: '8',  label: 'Desil 8' },
  { value: '9',  label: 'Desil 9' },
  { value: '10', label: 'Desil 10' },
]

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

const tabs = [
  { key: 'anggota',  label: 'Anggota',  icon: 'pi pi-users' },
  { key: 'keluarga', label: 'Keluarga', icon: 'pi pi-home' },
]
const activeTab = ref('anggota')

function switchTab(key) {
  if (activeTab.value === key) return
  activeTab.value = key
}

const currentProvinsi = computed(() =>
  activeTab.value === 'anggota' ? anggota.provinsi : keluarga.provinsi
)

const wilayahLoading  = ref(false)
const provinsiOptions = ref([])

function getProvinsiBps(slug) {
  return provinsiOptions.value.find(p => p.slug === slug)?.kode ?? null
}

async function loadWilayah() {
  wilayahLoading.value = true
  try {
    const list = await fetchBaselineProvinsi()
    provinsiOptions.value = list
    if (list.length > 0) {
      anggota.provinsi  = list[0].slug
      keluarga.provinsi = list[0].slug
      loadAnggotaKabkota(list[0].kode)
      loadKeluargaKabkota(list[0].kode)
      loadAnggota()
      loadKeluarga()
    }
  } catch (e) {
    console.error('[Wilayah] gagal load provinsi:', e)
  } finally {
    wilayahLoading.value = false
  }
}

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
  anggota.kabkota = ''; anggota.kecamatan = ''
  anggotaKecamatanOptions.value = []
  loadAnggotaKabkota(getProvinsiBps(anggota.provinsi))
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
  keluarga.kabkota = ''; keluarga.kecamatan = ''
  keluargaKecamatanOptions.value = []
  loadKeluargaKabkota(getProvinsiBps(keluarga.provinsi))
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

function makeTableState() {
  return reactive({
    loading: false, error: '',
    rows: [], columns: [],
    search: '', provinsi: '', kabkota: '', kecamatan: '', desil: '',
    historyStack: [], currentCursor: null,
    meta: {
      label: '', totalItems: 0, totalPages: 1, currentPage: 1,
      hasNextPage: false, hasPreviousPage: false, nextCursor: null, limit: 10,
    },
  })
}

const anggota  = makeTableState()
const keluarga = makeTableState()

const showFilter    = ref(false)
const filterLoading = ref(false)
const filterError   = ref('')
const filterFields  = ref([])

const anggotaFilters  = reactive({})
const keluargaFilters = reactive({})

const currentFilters = computed(() =>
  activeTab.value === 'anggota' ? anggotaFilters : keluargaFilters
)

/**
 * groupedFilterFields — semua grup, TIDAK termasuk field ternak
 * Grup yang seluruh isinya ternak akan kosong → disaring di computed ini
 * sehingga header grup "Ternak" dari DB tidak ikut muncul.
 */
const groupedFilterFieldsNoTernak = computed(() => {
  const groups = {}
  for (const f of filterFields.value) {
    if (isTernakField(f.field_key)) continue   // skip ternak — ditangani slider
    const g = f.field_group || ''
    if (!groups[g]) groups[g] = []
    groups[g].push(f)
  }
  // Buang grup kosong (seharusnya tidak terjadi, tapi aman)
  return Object.fromEntries(Object.entries(groups).filter(([, v]) => v.length > 0))
})

const activeFilterCount = computed(() => {
  const drawerCount = Object.values(currentFilters.value).filter(v => v !== '' && v != null).length
  const desilCount  = (activeTab.value === 'keluarga' && keluarga.desil) ? 1 : 0
  const ternakCount = activeTab.value === 'keluarga'
    ? TERNAK_FIELDS.filter(f => { const [mn, mx] = ternakSliders[f.key]; return !(mn === 0 && mx === 100) }).length
    : 0
  return drawerCount + desilCount + ternakCount
})

function formatFilterValue(val) {
  if (val instanceof Date) {
    const y = val.getFullYear()
    const m = String(val.getMonth() + 1).padStart(2, '0')
    const d = String(val.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
  }
  return String(val)
}

const activeFiltersBadges = computed(() => {
  const result = []
  if (activeTab.value === 'keluarga' && keluarga.desil) {
    const opt = desilOptions.find(o => o.value === keluarga.desil)
    result.push({ key: '__desil__', label: 'Desil', display: opt?.label ?? keluarga.desil })
  }
  if (activeTab.value === 'keluarga') {
    for (const tf of TERNAK_FIELDS) {
      const [mn, mx] = ternakSliders[tf.key]
      if (mn === 0 && mx === 100) continue
      result.push({ key: `__ternak__${tf.key}`, label: tf.label, display: `${mn} – ${mx}` })
    }
  }
  for (const f of filterFields.value) {
    if (isTernakField(f.field_key)) continue
    const val = currentFilters.value[f.field_key]
    if (val === '' || val == null) continue
    let display = formatFilterValue(val)
    if (f.refs?.length) {
      const ref = f.refs.find(r => r.ref_value === String(val))
      if (ref) display = ref.ref_label
    }
    result.push({ key: f.field_key, label: f.field_label, display })
  }
  return result
})

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
    const store = activeTab.value === 'anggota' ? anggotaFilters : keluargaFilters
    for (const f of data) {
      if (isTernakField(f.field_key)) continue
      if (!(f.field_key in store)) store[f.field_key] = ''
    }
  } catch (e) {
    filterError.value = 'Gagal memuat konfigurasi filter.'
    console.error('[DataBaseline] fetchFilterFields error:', e)
  } finally {
    filterLoading.value = false
  }
}

watch(activeTab, () => {
  filterFields.value = []
  if (currentProvinsi.value) loadFilterFields()
})

watch(showFilter, (val) => {
  if (val && filterFields.value.length === 0 && currentProvinsi.value) loadFilterFields()
})

function applyFilter() {
  showFilter.value = false
  activeTab.value === 'anggota' ? loadAnggota() : loadKeluarga()
}

function resetFilter() {
  const store = activeTab.value === 'anggota' ? anggotaFilters : keluargaFilters
  for (const k of Object.keys(store)) store[k] = ''
  if (activeTab.value === 'keluarga') {
    keluarga.desil = ''
    for (const tf of TERNAK_FIELDS) ternakSliders[tf.key] = [0, 100]
  }
  showFilter.value = false
  activeTab.value === 'anggota' ? loadAnggota() : loadKeluarga()
}

function clearOneFilter(fieldKey) {
  if (fieldKey === '__desil__') { keluarga.desil = ''; loadKeluarga(); return }
  if (fieldKey.startsWith('__ternak__')) {
    ternakSliders[fieldKey.replace('__ternak__', '')] = [0, 100]
    loadKeluarga(); return
  }
  const store = activeTab.value === 'anggota' ? anggotaFilters : keluargaFilters
  if (fieldKey in store) { store[fieldKey] = ''; applyFilter() }
}

function buildFilterParams(store) {
  const params = {}
  for (const [k, v] of Object.entries(store)) {
    if (v !== '' && v != null) params[k] = formatFilterValue(v)
  }
  return params
}

function buildTernakParams() {
  const params = {}
  for (const tf of TERNAK_FIELDS) {
    const val = sliderToApiValue(...ternakSliders[tf.key])
    if (val !== null) params[tf.key] = val
  }
  return params
}

async function loadAnggota(cursor = null) {
  if (!anggota.provinsi) return
  anggota.loading = true; anggota.error = ''
  try {
    const params = { provinsi: anggota.provinsi, cursor: cursor || undefined, search: anggota.search.trim() || undefined }
    if (anggota.kabkota)   params.kabkota_kode   = anggota.kabkota
    if (anggota.kecamatan) params.kecamatan_kode = anggota.kecamatan
    Object.assign(params, buildFilterParams(anggotaFilters))
    const res = await fetchBaselineAnggota(params)
    anggota.rows = res.data ?? []; anggota.columns = res.columns ?? []
    Object.assign(anggota.meta, res.meta ?? {})
    anggota.currentCursor = cursor
  } catch (e) {
    anggota.error = 'Gagal memuat: ' + (e?.response?.data?.error ?? e.message)
  } finally { anggota.loading = false }
}
function nextAnggota() { anggota.historyStack.push(anggota.currentCursor); loadAnggota(anggota.meta.nextCursor) }
function prevAnggota() { if (anggota.historyStack.length) loadAnggota(anggota.historyStack.pop()) }
function resetAnggota() {
  const first = provinsiOptions.value[0]
  anggota.provinsi = first?.slug ?? ''; anggota.kabkota = ''; anggota.kecamatan = ''; anggota.search = ''
  anggota.rows = []; anggota.columns = []; anggota.historyStack = []; anggota.currentCursor = null
  anggotaKabkotaOptions.value = []; anggotaKecamatanOptions.value = []
  for (const k of Object.keys(anggotaFilters)) anggotaFilters[k] = ''
  Object.assign(anggota.meta, { label:'', totalItems:0, totalPages:1, currentPage:1, hasNextPage:false, hasPreviousPage:false, nextCursor:null, limit:10 })
  if (first) { loadAnggotaKabkota(first.kode); loadAnggota() }
}

async function loadKeluarga(cursor = null) {
  if (!keluarga.provinsi) return
  keluarga.loading = true; keluarga.error = ''
  try {
    const params = { provinsi: keluarga.provinsi, cursor: cursor || undefined, search: keluarga.search.trim() || undefined }
    if (keluarga.kabkota)   params.kabkota_kode   = keluarga.kabkota
    if (keluarga.kecamatan) params.kecamatan_kode = keluarga.kecamatan
    if (keluarga.desil)     params.desil_nasional  = keluarga.desil
    Object.assign(params, buildTernakParams())
    Object.assign(params, buildFilterParams(keluargaFilters))
    const res = await fetchBaselineKeluarga(params)
    keluarga.rows = res.data ?? []; keluarga.columns = res.columns ?? []
    Object.assign(keluarga.meta, res.meta ?? {})
    keluarga.currentCursor = cursor
  } catch (e) {
    keluarga.error = 'Gagal memuat: ' + (e?.response?.data?.error ?? e.message)
  } finally { keluarga.loading = false }
}
function nextKeluarga() { keluarga.historyStack.push(keluarga.currentCursor); loadKeluarga(keluarga.meta.nextCursor) }
function prevKeluarga() { if (keluarga.historyStack.length) loadKeluarga(keluarga.historyStack.pop()) }
function resetKeluarga() {
  const first = provinsiOptions.value[0]
  keluarga.provinsi = first?.slug ?? ''; keluarga.kabkota = ''; keluarga.kecamatan = ''; keluarga.search = ''; keluarga.desil = ''
  keluarga.rows = []; keluarga.columns = []; keluarga.historyStack = []; keluarga.currentCursor = null
  keluargaKabkotaOptions.value = []; keluargaKecamatanOptions.value = []
  for (const k of Object.keys(keluargaFilters)) keluargaFilters[k] = ''
  for (const tf of TERNAK_FIELDS) ternakSliders[tf.key] = [0, 100]
  Object.assign(keluarga.meta, { label:'', totalItems:0, totalPages:1, currentPage:1, hasNextPage:false, hasPreviousPage:false, nextCursor:null, limit:10 })
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
