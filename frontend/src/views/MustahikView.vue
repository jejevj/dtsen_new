<template>
  <AppLayout>
    <div class="space-y-5">

      <!-- Header -->
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 class="text-xl font-bold text-slate-800">Data Mustahik</h2>
          <p class="text-sm text-slate-500 mt-0.5">Daftar penerima manfaat zakat · Desil 1–4</p>
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

      <!-- ===== TABEL DATA MUSTAHIK ===== -->
      <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">

        <!-- Toolbar: search global + badge filter aktif -->
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

        <!-- Loading -->
        <div v-if="tableLoading" class="flex justify-center items-center py-16 text-slate-400">
          <i class="pi pi-spin pi-spinner mr-2"></i> Memuat data…
        </div>

        <!-- Error -->
        <div v-else-if="tableError" class="py-12 text-center text-red-500 text-sm">
          <i class="pi pi-exclamation-circle text-2xl mb-2 block"></i>
          {{ tableError }}
        </div>

        <!-- Kosong -->
        <div v-else-if="rows.length === 0" class="py-16 text-center text-slate-400 text-sm">
          <i class="pi pi-inbox text-3xl mb-3 block opacity-30"></i>
          Tidak ada data mustahik yang sesuai filter.
        </div>

        <!-- Tabel -->
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <tr>
                <th class="px-5 py-3 text-left">No</th>
                <th class="px-5 py-3 text-left">Nama Lengkap</th>
                <th class="px-5 py-3 text-left">NIK</th>
                <th class="px-5 py-3 text-left">Jenis Kelamin</th>
                <th class="px-5 py-3 text-left">Kab/Kota</th>
                <th class="px-5 py-3 text-left">Desil</th>
                <th class="px-5 py-3 text-left">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr
                v-for="(row, i) in rows" :key="row.mustahik_id ?? i"
                class="hover:bg-slate-50 transition-colors"
              >
                <td class="px-5 py-3 text-slate-400">{{ (pagination.page - 1) * pagination.perPage + i + 1 }}</td>
                <td class="px-5 py-3 font-medium text-slate-800">{{ row.nama_lengkap ?? '-' }}</td>
                <td class="px-5 py-3 text-slate-600 font-mono text-xs">{{ row.nik_hashed ?? '-' }}</td>
                <td class="px-5 py-3">
                  <span
                    :class="row.jenis_kelamin === 'm' ? 'bg-blue-50 text-blue-700' : 'bg-pink-50 text-pink-700'"
                    class="px-2 py-0.5 rounded-full text-xs font-semibold"
                  >
                    {{ row.jenis_kelamin === 'm' ? 'Laki-laki' : 'Perempuan' }}
                  </span>
                </td>
                <td class="px-5 py-3 text-slate-600">{{ row.kabkota_nama ?? '-' }}</td>
                <td class="px-5 py-3">
                  <span class="px-2 py-0.5 rounded-full text-xs font-bold bg-green-50 text-green-700">
                    Desil {{ row.desil ?? '-' }}
                  </span>
                </td>
                <td class="px-5 py-3">
                  <Button
                    icon="pi pi-eye"
                    text rounded size="small"
                    class="text-primary-600"
                    @click="$router.push('/mustahik/' + row.nik_hashed)"
                    v-tooltip="'Lihat Detail'"
                  />
                </td>
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

            <!-- Loading konfigurasi -->
            <div v-if="filterLoading" class="flex items-center gap-2 text-slate-400 text-sm py-4">
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
                    v-model="activeFilters[field.field_key]"
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
                    v-model="activeFilters[field.field_key]"
                    :placeholder="field.field_label"
                    class="w-full"
                    :min-fraction-digits="field.field_type === 'Float' ? 2 : 0"
                    :max-fraction-digits="field.field_type === 'Float' ? 2 : 0"
                  />

                  <!-- Tanggal -->
                  <DatePicker
                    v-else-if="field.field_type === 'Date'"
                    v-model="activeFilters[field.field_key]"
                    :placeholder="field.field_label"
                    date-format="dd/mm/yy"
                    class="w-full"
                    show-button-bar
                  />

                  <!-- Teks -->
                  <InputText
                    v-else
                    v-model="activeFilters[field.field_key]"
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
import { fetchFilterFields } from '@/services/tampilanDtsenService'
import api                   from '@/services/api'

// ── Drawer state ──────────────────────────────────────────────────────────────
const showFilter    = ref(false)
const filterLoading = ref(false)
const filterError   = ref('')
const filterFields  = ref([])
const activeFilters = reactive({})
const globalSearch  = ref('')

const activeFilterCount = computed(() =>
  Object.values(activeFilters).filter(v => v !== '' && v != null).length
)

const groupedFilterFields = computed(() => {
  const groups = {}
  for (const f of filterFields.value) {
    const g = f.field_group || ''
    if (!groups[g]) groups[g] = []
    groups[g].push(f)
  }
  return groups
})

// Hanya load filter kategori individu untuk halaman ini
async function loadFilterFields() {
  filterLoading.value = true
  filterError.value   = ''
  try {
    const data = await fetchFilterFields('individu')
    filterFields.value = data
    for (const f of data) {
      if (!(f.field_key in activeFilters)) activeFilters[f.field_key] = ''
    }
  } catch (e) {
    filterError.value = 'Gagal memuat konfigurasi filter.'
    console.error('[TampilanDtsen] fetchFilterFields error:', e)
  } finally {
    filterLoading.value = false
  }
}

// ── Tabel ─────────────────────────────────────────────────────────────────────
const tableLoading = ref(false)
const tableError   = ref('')
const rows         = ref([])
const pagination   = reactive({ page: 1, perPage: 20, total: 0, totalPages: 1 })

async function fetchMustahik(page = 1) {
  tableLoading.value = true
  tableError.value   = ''
  try {
    const params = { page, per_page: pagination.perPage }
    if (globalSearch.value.trim()) params.nama = globalSearch.value.trim()
    for (const [k, v] of Object.entries(activeFilters)) {
      if (v !== '' && v != null) params[k] = v
    }
    const res = await api.get('/mustahik', { params })
    const d   = res.data
    rows.value            = d.data        ?? d.items ?? []
    pagination.page       = d.meta?.page        ?? page
    pagination.total      = d.meta?.total       ?? rows.value.length
    pagination.totalPages = d.meta?.pages       ?? 1
  } catch (e) {
    tableError.value = 'Gagal memuat data mustahik: ' + (e?.response?.data?.message ?? e.message)
    console.error('[Mustahik] fetchMustahik error:', e)
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
  for (const k of Object.keys(activeFilters)) activeFilters[k] = ''
  globalSearch.value = ''
  pagination.page    = 1
  fetchMustahik(1)
}

function changePage(p) { fetchMustahik(p) }

onMounted(() => {
  loadFilterFields()
  fetchMustahik(1)
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
</style>
