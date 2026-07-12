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
                option-label="label" option-value="kode"
                placeholder="Pilih Provinsi…"
                class="w-full text-sm" :loading="wilayahLoading"
                filter show-clear
                @change="onProvinsiChange"
              />
            </div>

            <!-- Kabkota (muncul jika skala 1=nasional atau 2=provinsi) -->
            <div v-if="showKabkota" class="flex flex-col gap-1 min-w-[220px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Kabupaten / Kota</label>
              <Select
                v-model="anggota.kabkota"
                :options="kabkotaOptions"
                option-label="nama" option-value="kode"
                placeholder="Semua Kab/Kota"
                class="w-full text-sm" :loading="kabkotaLoading"
                filter show-clear
                @change="onKabkotaChange"
              />
            </div>

            <!-- Kecamatan (muncul jika kabkota dipilih atau skala 3) -->
            <div v-if="showKecamatan" class="flex flex-col gap-1 min-w-[220px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Kecamatan</label>
              <Select
                v-model="anggota.kecamatan"
                :options="kecamatanOptions"
                option-label="nama" option-value="kode"
                placeholder="Semua Kecamatan"
                class="w-full text-sm" :loading="kecamatanLoading"
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
                :disabled="!anggota.provinsi" :loading="anggota.loading"
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
          :loading="anggota.loading" :error="anggota.error"
          :rows="anggota.rows" :columns="anggota.columns"
          :meta="anggota.meta" :history-stack="anggota.historyStack"
          :empty-hint="!anggota.provinsi ? 'Pilih provinsi untuk menampilkan data anggota.' : 'Tidak ada data yang sesuai.'"
          title="Data Anggota"
          @next="nextAnggota" @prev="prevAnggota"
        />
      </template>

      <!-- TAB KELUARGA -->
      <template v-if="activeTab === 'keluarga'">
        <div class="bg-white border border-slate-200 rounded-2xl shadow-sm px-5 py-4">
          <div class="flex flex-wrap items-end gap-4">
            <div class="flex flex-col gap-1 flex-1 min-w-[180px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Cari (halaman ini)</label>
              <InputText v-model="keluarga.search" placeholder="No. KK / Nama…" class="text-sm w-full" @keyup.enter="loadKeluarga()" />
            </div>
            <div class="flex gap-2 pb-0.5">
              <Button label="Cari" icon="pi pi-search" size="small" :loading="keluarga.loading" @click="loadKeluarga()" />
              <Button label="Reset" icon="pi pi-times" size="small" severity="secondary" outlined @click="resetKeluarga" />
            </div>
          </div>
        </div>
        <BaselineTable
          :loading="keluarga.loading" :error="keluarga.error"
          :rows="keluarga.rows" :columns="keluarga.columns"
          :meta="keluarga.meta" :history-stack="keluarga.historyStack"
          empty-hint="Memuat data keluarga…"
          title="Data Keluarga"
          @next="nextKeluarga" @prev="prevKeluarga"
        />
      </template>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import AppLayout     from '@/components/layout/AppLayout.vue'
import BaselineTable from '@/components/baseline/BaselineTable.vue'
import Button        from 'primevue/button'
import InputText     from 'primevue/inputtext'
import Select        from 'primevue/select'
import {
  fetchWilayahDropdown,
  fetchKabkota,
  fetchKecamatan,
  fetchBaselineAnggota,
  fetchBaselineKeluarga,
} from '@/services/baselineService'

// ── Tabs ──────────────────────────────────────────────────────
const tabs = [
  { key: 'anggota',  label: 'Anggota',  icon: 'pi pi-users' },
  { key: 'keluarga', label: 'Keluarga', icon: 'pi pi-home' },
]
const activeTab = ref('anggota')
const keluargaLoaded = ref(false)
function switchTab(key) {
  activeTab.value = key
  if (key === 'keluarga' && !keluargaLoaded.value) {
    keluargaLoaded.value = true
    loadKeluarga()
  }
}

// ── Wilayah dropdown state ────────────────────────────────────
const wilayahLoading   = ref(false)
const kabkotaLoading   = ref(false)
const kecamatanLoading = ref(false)

const skala           = ref(0)   // 1=nasional, 2=provinsi, 3=kabkota
const provinsiOptions = ref([])  // [{ kode, label }]
const kabkotaOptions  = ref([])  // [{ kode, nama, provinsi_kode }]
const kecamatanOptions = ref([]) // [{ kode, nama, kabkota_kode }]

// Kapan dropdown kabkota & kecamatan muncul
const showKabkota   = computed(() => anggota.provinsi)
const showKecamatan = computed(() => anggota.kabkota || skala.value === 3)

// ── Load wilayah saat mount ────────────────────────────────────
async function loadWilayah() {
  wilayahLoading.value = true
  try {
    const res = await fetchWilayahDropdown()
    skala.value = res.skala ?? 0

    // Normalisasi provinsi options: backend bisa kirim {kode, nama} atau {kode, label}
    provinsiOptions.value = (res.provinsi ?? []).map(p => ({
      kode:  p.kode,
      label: p.nama ?? p.label,
    }))

    // Skala 3 (kabkota): langsung isi kabkota & kecamatan dari response awal
    if (skala.value === 3) {
      kabkotaOptions.value  = res.kabkota  ?? []
      kecamatanOptions.value = res.kecamatan ?? []
      // Auto-set provinsi & kabkota jika hanya 1 pilihan
      if (provinsiOptions.value.length === 1)
        anggota.provinsi = provinsiOptions.value[0].kode
      if (kabkotaOptions.value.length === 1)
        anggota.kabkota = kabkotaOptions.value[0].kode
    }
  } catch (e) {
    console.error('[Wilayah] gagal load dropdown:', e)
  } finally {
    wilayahLoading.value = false
  }
}

// ── Saat provinsi dipilih → load kabkota ──────────────────────
async function onProvinsiChange() {
  anggota.kabkota    = ''
  anggota.kecamatan  = ''
  kabkotaOptions.value  = []
  kecamatanOptions.value = []

  if (!anggota.provinsi) return

  kabkotaLoading.value = true
  try {
    kabkotaOptions.value = await fetchKabkota(anggota.provinsi)
  } catch (e) {
    console.error('[Wilayah] gagal load kabkota:', e)
  } finally {
    kabkotaLoading.value = false
  }
}

// ── Saat kabkota dipilih → load kecamatan ─────────────────────
async function onKabkotaChange() {
  anggota.kecamatan = ''
  kecamatanOptions.value = []

  if (!anggota.kabkota) return

  kecamatanLoading.value = true
  try {
    kecamatanOptions.value = await fetchKecamatan(anggota.kabkota)
  } catch (e) {
    console.error('[Wilayah] gagal load kecamatan:', e)
  } finally {
    kecamatanLoading.value = false
  }
}

// ── Table state factory ────────────────────────────────────────
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

// ── Anggota ───────────────────────────────────────────────────
async function loadAnggota(cursor = null) {
  if (!anggota.provinsi) return
  anggota.loading = true; anggota.error = ''
  try {
    const params = {
      provinsi: anggota.provinsi,
      cursor:   cursor || undefined,
      search:   anggota.search.trim() || undefined,
    }
    // Kirim filter kabkota & kecamatan ke backend jika dipilih
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
  anggota.provinsi  = ''
  anggota.kabkota   = ''
  anggota.kecamatan = ''
  anggota.search    = ''
  anggota.rows = []; anggota.columns = []
  anggota.historyStack = []; anggota.currentCursor = null
  kabkotaOptions.value   = []
  kecamatanOptions.value = []
  Object.assign(anggota.meta, {
    label:'', totalItems:0, totalPages:1, currentPage:1,
    hasNextPage:false, hasPreviousPage:false, nextCursor:null, limit:10,
  })
}

// ── Keluarga ──────────────────────────────────────────────────
async function loadKeluarga(cursor = null) {
  keluarga.loading = true; keluarga.error = ''
  try {
    const res = await fetchBaselineKeluarga({
      cursor: cursor || undefined,
      search: keluarga.search.trim() || undefined,
    })
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
  keluarga.search = ''
  keluarga.rows = []; keluarga.columns = []
  keluarga.historyStack = []; keluarga.currentCursor = null
  keluargaLoaded.value = false
  Object.assign(keluarga.meta, {
    label:'', totalItems:0, totalPages:1, currentPage:1,
    hasNextPage:false, hasPreviousPage:false, nextCursor:null, limit:10,
  })
}

onMounted(() => loadWilayah())
</script>
