<template>
  <AppLayout>
    <div class="space-y-5">

      <!-- Header -->
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 class="text-xl font-bold text-slate-800">Data Baseline</h2>
          <p class="text-sm text-slate-500 mt-0.5">Data baseline penerima manfaat ZAWA · Sumber: Kemenag</p>
        </div>
      </div>

      <!-- Filter Bar -->
      <div class="bg-white border border-slate-200 rounded-2xl shadow-sm px-5 py-4">
        <div class="flex flex-wrap items-end gap-4">

          <!-- Pilih Provinsi -->
          <div class="flex flex-col gap-1 min-w-[220px]">
            <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Provinsi</label>
            <Select
              v-model="selectedProvinsi"
              :options="provinsiOptions"
              option-label="label"
              option-value="kode"
              placeholder="Pilih Provinsi…"
              class="w-full text-sm"
              :loading="provinsiLoading"
              filter
              show-clear
            />
          </div>

          <!-- Search -->
          <div class="flex flex-col gap-1 flex-1 min-w-[180px]">
            <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Cari (di halaman ini)</label>
            <InputText
              v-model="search"
              placeholder="Nama / NIK…"
              class="text-sm w-full"
              @keyup.enter="() => load()"
            />
          </div>

          <!-- Tombol -->
          <div class="flex gap-2 pb-0.5">
            <Button
              label="Tampilkan"
              icon="pi pi-search"
              size="small"
              :disabled="!selectedProvinsi"
              :loading="tableLoading"
              @click="() => load()"
            />
            <Button
              label="Reset"
              icon="pi pi-times"
              size="small"
              severity="secondary"
              outlined
              @click="reset"
            />
          </div>
        </div>
      </div>

      <!-- Tabel -->
      <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">

        <!-- Toolbar -->
        <div class="flex items-center justify-between gap-3 px-5 py-3 border-b border-slate-100">
          <div class="flex items-center gap-2">
            <i class="pi pi-database text-slate-400"></i>
            <span class="text-sm font-semibold text-slate-700">
              {{ meta.label ? `Data Baseline · ${meta.label}` : 'Data Baseline' }}
            </span>
            <span
              v-if="meta.totalItems > 0"
              class="ml-1 px-2 py-0.5 bg-primary-50 text-primary-700 border border-primary-200 text-xs font-semibold rounded-full"
            >{{ meta.totalItems.toLocaleString('id-ID') }} total data</span>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="tableLoading" class="flex justify-center items-center py-16 text-slate-400">
          <i class="pi pi-spin pi-spinner mr-2"></i> Memuat data…
        </div>

        <!-- Error -->
        <div v-else-if="tableError" class="py-12 text-center text-red-500 text-sm">
          <i class="pi pi-exclamation-circle text-2xl mb-2 block"></i>
          {{ tableError }}
        </div>

        <!-- Belum pilih provinsi -->
        <div v-else-if="!selectedProvinsi && rows.length === 0" class="py-20 text-center text-slate-400 text-sm">
          <i class="pi pi-map-marker text-4xl mb-3 block opacity-30"></i>
          Pilih provinsi terlebih dahulu untuk menampilkan data.
        </div>

        <!-- Kosong -->
        <div v-else-if="rows.length === 0" class="py-16 text-center text-slate-400 text-sm">
          <i class="pi pi-inbox text-3xl mb-3 block opacity-30"></i>
          Tidak ada data yang sesuai.
        </div>

        <!-- Tabel dinamis -->
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <tr>
                <th class="px-4 py-3 text-left whitespace-nowrap">No</th>
                <th
                  v-for="col in columns"
                  :key="col"
                  class="px-4 py-3 text-left whitespace-nowrap"
                >{{ formatColLabel(col) }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr
                v-for="(row, i) in rows"
                :key="i"
                class="hover:bg-slate-50 transition-colors"
              >
                <td class="px-4 py-2.5 text-slate-400 text-xs">
                  {{ (meta.currentPage - 1) * meta.limit + i + 1 }}
                </td>
                <td
                  v-for="col in columns"
                  :key="col"
                  class="px-4 py-2.5 text-slate-700 max-w-[240px] truncate"
                  :title="String(row[col] ?? '')"
                >{{ row[col] ?? '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div
          v-if="rows.length > 0"
          class="flex items-center justify-between px-5 py-3 border-t border-slate-100"
        >
          <span class="text-xs text-slate-400">
            Halaman {{ meta.currentPage }} dari {{ meta.totalPages.toLocaleString('id-ID') }}
            · Total {{ meta.totalItems.toLocaleString('id-ID') }} data
          </span>
          <div class="flex gap-1">
            <Button
              icon="pi pi-angle-left"
              text rounded size="small"
              :disabled="!meta.hasPreviousPage || historyStack.length === 0"
              @click="() => prevPage()"
            />
            <Button
              icon="pi pi-angle-right"
              text rounded size="small"
              :disabled="!meta.hasNextPage"
              @click="() => nextPage()"
            />
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import AppLayout   from '@/components/layout/AppLayout.vue'
import Button      from 'primevue/button'
import InputText   from 'primevue/inputtext'
import Select      from 'primevue/select'
import { fetchBaselineProvinsi, fetchBaselineData } from '@/services/baselineService'

// ── Provinsi ───────────────────────────────────────────────────────────────────
const provinsiOptions = ref([])
const provinsiLoading = ref(false)
async function loadProvinsi() {
  provinsiLoading.value = true
  try { provinsiOptions.value = await fetchBaselineProvinsi() }
  catch (e) { console.error(e) }
  finally { provinsiLoading.value = false }
}

// ── Filter ───────────────────────────────────────────────────────────────────
const selectedProvinsi = ref('')
const search           = ref('')

// ── Tabel ───────────────────────────────────────────────────────────────────
const tableLoading = ref(false)
const tableError   = ref('')
const rows         = ref([])
const columns      = ref([])

// Cursor history untuk navigasi prev
const historyStack = ref([])  // stack cursor lama
const currentCursor = ref(null)

const meta = reactive({
  label: '', provinsi: '',
  totalItems: 0, totalPages: 1, currentPage: 1,
  hasNextPage: false, hasPreviousPage: false,
  nextCursor: null, limit: 10,
})

async function load(cursor = null) {
  if (!selectedProvinsi.value) return
  tableLoading.value = true
  tableError.value   = ''
  try {
    const res = await fetchBaselineData({
      provinsi: selectedProvinsi.value,
      cursor:   cursor || undefined,
      search:   search.value.trim() || undefined,
    })
    rows.value    = res.data    ?? []
    columns.value = res.columns ?? []
    Object.assign(meta, res.meta ?? {})
    currentCursor.value = cursor
  } catch (e) {
    tableError.value = 'Gagal memuat data: ' + (e?.response?.data?.error ?? e.message)
  } finally {
    tableLoading.value = false
  }
}

function nextPage() {
  if (!meta.hasNextPage) return
  historyStack.value.push(currentCursor.value)  // simpan cursor saat ini
  load(meta.nextCursor)
}

function prevPage() {
  if (historyStack.value.length === 0) return
  const prevCursor = historyStack.value.pop()
  load(prevCursor)
}

function reset() {
  selectedProvinsi.value = ''
  search.value           = ''
  rows.value             = []
  columns.value          = []
  historyStack.value     = []
  currentCursor.value    = null
  Object.assign(meta, {
    label: '', provinsi: '', totalItems: 0, totalPages: 1,
    currentPage: 1, hasNextPage: false, hasPreviousPage: false,
    nextCursor: null, limit: 10,
  })
}

function formatColLabel(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

onMounted(() => loadProvinsi())
</script>
