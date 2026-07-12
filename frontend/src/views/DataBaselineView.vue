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
            <div class="flex flex-col gap-1 min-w-[220px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Provinsi</label>
              <Select
                v-model="anggota.provinsi"
                :options="provinsiOptions"
                option-label="label" option-value="kode"
                placeholder="Pilih Provinsi…"
                class="w-full text-sm" :loading="provinsiLoading"
                filter show-clear
              />
            </div>
            <div class="flex flex-col gap-1 flex-1 min-w-[180px]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Cari (halaman ini)</label>
              <InputText v-model="anggota.search" placeholder="Nama / NIK…" class="text-sm w-full" @keyup.enter="loadAnggota()" />
            </div>
            <div class="flex gap-2 pb-0.5">
              <Button label="Tampilkan" icon="pi pi-search" size="small" :disabled="!anggota.provinsi" :loading="anggota.loading" @click="loadAnggota()" />
              <Button label="Reset" icon="pi pi-times" size="small" severity="secondary" outlined @click="resetAnggota" />
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
import { ref, reactive, onMounted, watch } from 'vue'
import AppLayout     from '@/components/layout/AppLayout.vue'
import BaselineTable from '@/components/baseline/BaselineTable.vue'
import Button        from 'primevue/button'
import InputText     from 'primevue/inputtext'
import Select        from 'primevue/select'
import {
  fetchBaselineProvinsi,
  fetchBaselineAnggota,
  fetchBaselineKeluarga,
} from '@/services/baselineService'

const tabs = [
  { key: 'anggota',  label: 'Anggota',  icon: 'pi pi-users' },
  { key: 'keluarga', label: 'Keluarga', icon: 'pi pi-home' },
]
const activeTab = ref('anggota')

// Auto-load keluarga pertama kali saat tab dibuka
const keluargaLoaded = ref(false)
function switchTab(key) {
  activeTab.value = key
  if (key === 'keluarga' && !keluargaLoaded.value) {
    keluargaLoaded.value = true
    loadKeluarga()
  }
}

// Provinsi
const provinsiOptions = ref([])
const provinsiLoading = ref(false)
async function loadProvinsi() {
  provinsiLoading.value = true
  try { provinsiOptions.value = await fetchBaselineProvinsi() }
  catch (e) { console.error(e) }
  finally { provinsiLoading.value = false }
}

function makeTableState() {
  return reactive({
    loading: false, error: '', rows: [], columns: [],
    search: '', provinsi: '',
    historyStack: [], currentCursor: null,
    meta: {
      label: '', totalItems: 0, totalPages: 1, currentPage: 1,
      hasNextPage: false, hasPreviousPage: false, nextCursor: null, limit: 10,
    },
  })
}

const anggota  = makeTableState()
const keluarga = makeTableState()

// Anggota
async function loadAnggota(cursor = null) {
  if (!anggota.provinsi) return
  anggota.loading = true; anggota.error = ''
  try {
    const res = await fetchBaselineAnggota({
      provinsi: anggota.provinsi,
      cursor:   cursor || undefined,
      search:   anggota.search.trim() || undefined,
    })
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
  anggota.provinsi = ''; anggota.search = ''
  anggota.rows = []; anggota.columns = []; anggota.historyStack = []; anggota.currentCursor = null
  Object.assign(anggota.meta, { label:'', totalItems:0, totalPages:1, currentPage:1, hasNextPage:false, hasPreviousPage:false, nextCursor:null, limit:10 })
}

// Keluarga
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
function nextKeluarga() { keluarga.historyStack.push(keluarga.currentCursor); loadKeluarga(keluarga.meta.nextCursor) }
function prevKeluarga() { if (keluarga.historyStack.length) loadKeluarga(keluarga.historyStack.pop()) }
function resetKeluarga() {
  keluarga.search = ''
  keluarga.rows = []; keluarga.columns = []; keluarga.historyStack = []; keluarga.currentCursor = null
  keluargaLoaded.value = false
  Object.assign(keluarga.meta, { label:'', totalItems:0, totalPages:1, currentPage:1, hasNextPage:false, hasPreviousPage:false, nextCursor:null, limit:10 })
}

onMounted(() => loadProvinsi())
</script>
