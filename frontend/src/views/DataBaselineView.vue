<template>
  <AppLayout>
    <div class="space-y-5">

      <!-- Header -->
      <div>
        <h2 class="text-xl font-bold text-slate-800">Data Baseline</h2>
        <p class="text-sm text-slate-500 mt-0.5">Data baseline penerima manfaat ZAWA &middot; Sumber: Kemenag</p>
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
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout     from '@/components/layout/AppLayout.vue'
import BaselineTable from '@/components/baseline/BaselineTable.vue'
import Button        from 'primevue/button'
import InputText     from 'primevue/inputtext'
import Select        from 'primevue/select'
import {
  fetchBaselineProvinsi,
  fetchKabkotaByBps,
  fetchKecamatan,
  fetchBaselineAnggota,
  fetchBaselineKeluarga,
} from '@/services/baselineService'

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
function switchTab(key) { activeTab.value = key }

// ── Provinsi (shared)
// provinsiOptions: [{ kode, label, slug }, ...] dari /baseline/provinsi
const wilayahLoading  = ref(false)
const provinsiOptions = ref([])

/**
 * Cari entry provinsi dari provinsiOptions berdasarkan slug.
 * Dipakai untuk mendapatkan bps_kode saat load kabkota.
 */
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
      // Default ke slug provinsi pertama (sudah diurutkan alphabetical by label)
      const defaultSlug = list[0].slug
      const defaultBps  = list[0].kode
      anggota.provinsi  = defaultSlug
      keluarga.provinsi = defaultSlug
      // Load kabkota dropdown di background menggunakan bps_kode
      loadAnggotaKabkota(defaultBps)
      loadKeluargaKabkota(defaultBps)
      // Langsung load data — kirim slug ke API
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

/**
 * Load kabkota untuk tab Anggota.
 * @param {string} bpsKode  - kode BPS provinsi 2 digit ("32", "31", dst)
 */
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
  // Cari bps_kode dari slug yang dipilih
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

// ── Anggota
async function loadAnggota(cursor = null) {
  if (!anggota.provinsi) return
  anggota.loading = true; anggota.error = ''
  try {
    // Kirim slug ke backend — backend sudah support slug via _resolve_provinsi
    const params = {
      provinsi: anggota.provinsi,
      cursor:   cursor || undefined,
      search:   anggota.search.trim() || undefined,
    }
    if (anggota.kabkota)   params.kabkota_kode   = anggota.kabkota
    if (anggota.kecamatan) params.kecamatan_kode = anggota.kecamatan
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
  Object.assign(anggota.meta, {
    label:'', totalItems:0, totalPages:1, currentPage:1,
    hasNextPage:false, hasPreviousPage:false, nextCursor:null, limit:10,
  })
  if (first) { loadAnggotaKabkota(first.kode); loadAnggota() }
}

// ── Keluarga
async function loadKeluarga(cursor = null) {
  keluarga.loading = true; keluarga.error = ''
  try {
    const params = {
      cursor: cursor || undefined,
      search: keluarga.search.trim() || undefined,
    }
    if (keluarga.provinsi)  params.provinsi       = keluarga.provinsi
    if (keluarga.kabkota)   params.kabkota_kode   = keluarga.kabkota
    if (keluarga.kecamatan) params.kecamatan_kode = keluarga.kecamatan
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
  Object.assign(keluarga.meta, {
    label:'', totalItems:0, totalPages:1, currentPage:1,
    hasNextPage:false, hasPreviousPage:false, nextCursor:null, limit:10,
  })
  if (first) { loadKeluargaKabkota(first.kode); loadKeluarga() }
}

onMounted(() => loadWilayah())
</script>
